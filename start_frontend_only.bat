@echo off
echo ========================================
echo Starting Fraud Detection SaaS Frontend
echo ========================================
echo.
echo Installing dependencies...
cd frontend
call npm install
echo.
echo Starting React development server...
echo Frontend will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo ========================================
call npm run dev
