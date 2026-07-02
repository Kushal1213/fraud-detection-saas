from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    api_key: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Dataset Schemas
class DatasetBase(BaseModel):
    name: str


class DatasetCreate(DatasetBase):
    pass


class DatasetResponse(DatasetBase):
    id: int
    filename: str
    file_size: Optional[int] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analysis Schemas
class AnalysisBase(BaseModel):
    dataset_id: int


class AnalysisCreate(AnalysisBase):
    pass


class AnalysisResponse(AnalysisBase):
    id: int
    status: str
    total_transactions: Optional[int] = None
    fraud_count: Optional[int] = None
    fraud_rate: Optional[float] = None
    avg_fraud_score: Optional[float] = None
    auroc_score: Optional[float] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    shap_explanations: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Prediction Schemas
class TransactionPrediction(BaseModel):
    transaction_id: str
    fraud_probability: float
    is_fraud: bool
    confidence: str
    shap_explanation: Optional[Dict[str, float]] = None


class BatchPredictionResponse(BaseModel):
    analysis_id: int
    status: str
    total_transactions: int
    fraud_count: int
    fraud_rate: float
    predictions: List[TransactionPrediction]
    processing_time: float


# API Response Schemas
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
