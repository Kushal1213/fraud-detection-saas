@echo off
echo ========================================
echo Installing Backend Dependencies
echo ========================================
cd backend
pip install -r requirements.txt
echo.
echo ========================================
echo Starting FastAPI Backend Server
echo ========================================
echo Backend will run on: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
