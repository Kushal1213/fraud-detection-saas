@echo off
echo ========================================
echo Starting Fraud Detection SaaS Backend
echo ========================================
echo.
echo Installing dependencies...
cd backend
pip install -r requirements.txt
echo.
echo Starting FastAPI server on http://localhost:8000
echo API Docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
