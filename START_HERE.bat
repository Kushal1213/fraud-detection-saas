@echo off
echo ========================================
echo   Fraud Detection SaaS - Local Setup
echo ========================================
echo.
echo This will help you start the application locally.
echo You need to run TWO terminals (command prompts).
echo.
echo ========================================
echo STEP 1: Start Backend (Terminal 1)
echo ========================================
echo.
echo 1. Open a new command prompt
echo 2. Run: start_backend_only.bat
echo 3. Wait for: "Uvicorn running on http://0.0.0.0:8000"
echo 4. Keep this terminal OPEN
echo.
echo ========================================
echo STEP 2: Start Frontend (Terminal 2)
echo ========================================
echo.
echo 1. Open ANOTHER command prompt
echo 2. Run: start_frontend_only.bat
echo 3. Wait for: "Local: http://localhost:5173/"
echo 4. Keep this terminal OPEN
echo.
echo ========================================
echo STEP 3: Access Application
echo ========================================
echo.
echo Open your browser and go to:
echo http://localhost:5173
echo.
echo ========================================
echo Testing Instructions
echo ========================================
echo.
echo 1. Register a new account
echo 2. Upload the demo_transactions.csv file
echo 3. View the analysis results
echo.
echo For detailed instructions, see RUN_LOCAL.md
echo.
echo ========================================
echo Press any key to open Step 1 (Backend)...
pause > nul
start cmd /k start_backend_only.bat
