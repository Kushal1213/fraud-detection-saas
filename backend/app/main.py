from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import pandas as pd
import io
import uuid
from pathlib import Path
from typing import List

from app.config import settings
from app.database import engine, get_db, Base
from app.models import User, Dataset, Analysis
from app.schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    DatasetCreate, DatasetResponse, AnalysisCreate, AnalysisResponse,
    TransactionPrediction, BatchPredictionResponse, MessageResponse, HealthResponse
)
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, generate_api_key
)
from app.ml_service import fraud_service

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered fraud detection SaaS API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        model_loaded=fraud_service.detector is not None
    )


# Authentication endpoints
@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        api_key=generate_api_key()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse.from_orm(db_user)
    )


@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse.from_orm(user)
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return UserResponse.from_orm(current_user)


# Dataset endpoints
@app.post("/datasets", response_model=DatasetResponse)
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Validate file
    if not file.filename.endswith(('.csv', '.xlsx', '.json')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only CSV, XLSX, and JSON are supported."
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Create upload directory
    upload_dir = Path("uploads") / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Try to read the file to get row/column count
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(content))
        else:
            df = pd.read_json(io.BytesIO(content))
        
        row_count = len(df)
        column_count = len(df.columns)
        
        if row_count > settings.MAX_DATASET_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dataset exceeds maximum allowed size of {settings.MAX_DATASET_SIZE} rows"
            )
        
    except Exception as e:
        # If we can't read the file, still save it but mark row/column count as None
        row_count = None
        column_count = None
    
    # Create dataset record
    dataset = Dataset(
        user_id=current_user.id,
        name=name or file.filename,
        filename=file.filename,
        file_size=file_size,
        row_count=row_count,
        column_count=column_count,
        file_path=str(file_path),
        status="uploaded"
    )
    
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    
    return DatasetResponse.from_orm(dataset)


@app.get("/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    datasets = db.query(Dataset).filter(Dataset.user_id == current_user.id).all()
    return [DatasetResponse.from_orm(ds) for ds in datasets]


@app.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return DatasetResponse.from_orm(dataset)


# Analysis endpoints
@app.post("/analyses", response_model=AnalysisResponse)
async def create_analysis(
    analysis: AnalysisCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify dataset belongs to user
    dataset = db.query(Dataset).filter(
        Dataset.id == analysis.dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Create analysis record
    db_analysis = Analysis(
        user_id=current_user.id,
        dataset_id=analysis.dataset_id,
        status="pending"
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    # Add background task to process the analysis
    background_tasks.add_task(process_analysis, db_analysis.id, str(dataset.file_path))
    
    return AnalysisResponse.from_orm(db_analysis)


@app.get("/analyses", response_model=List[AnalysisResponse])
async def list_analyses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).all()
    return [AnalysisResponse.from_orm(analysis) for analysis in analyses]


@app.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return AnalysisResponse.from_orm(analysis)


# Prediction endpoints
@app.post("/predict", response_model=TransactionPrediction)
async def predict_single(
    transaction_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Make a prediction for a single transaction."""
    try:
        result = fraud_service.predict_single(transaction_data)
        
        # Get SHAP explanation
        shap_exp = fraud_service.get_shap_explanation(transaction_data)
        
        return TransactionPrediction(
            transaction_id=str(uuid.uuid4()),
            fraud_probability=result["fraud_probability"],
            is_fraud=result["is_fraud"],
            confidence=result["confidence"],
            shap_explanation=shap_exp
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


# Background task function
async def process_analysis(analysis_id: int, file_path: str):
    """Process dataset analysis in background."""
    from app.database import SessionLocal
    import time
    
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Get analysis record
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return
        
        # Update status to processing
        analysis.status = "processing"
        db.commit()
        
        # Load dataset
        file_path_obj = Path(file_path)
        if file_path_obj.suffix == '.csv':
            df = pd.read_csv(file_path_obj)
        elif file_path_obj.suffix == '.xlsx':
            df = pd.read_excel(file_path_obj)
        else:
            df = pd.read_json(file_path_obj)
        
        # Run predictions
        fraud_probs, metrics = fraud_service.predict_batch(df)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update analysis with results
        analysis.status = "completed"
        analysis.total_transactions = metrics["total_transactions"]
        analysis.fraud_count = metrics["fraud_count"]
        analysis.fraud_rate = metrics["fraud_rate"]
        analysis.avg_fraud_score = metrics["avg_fraud_score"]
        analysis.processing_time = processing_time
        analysis.results = {
            "predictions": fraud_probs.tolist(),
            "metrics": metrics
        }
        analysis.completed_at = pd.Timestamp.now()
        
        db.commit()
        
    except Exception as e:
        # Update status to failed
        analysis.status = "failed"
        analysis.error_message = str(e)
        db.commit()
        
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
