@echo off
echo ========================================
echo   DEPLOY TO RENDER - STEP BY STEP
echo ========================================
echo.
echo This script will help you deploy your project to Render.
echo Follow each step carefully.
echo.
echo ========================================
echo STEP 1: Initialize Git Repository
echo ========================================
echo.
git init
if %errorlevel% neq 0 (
    echo Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)
echo [OK] Git repository initialized
echo.
echo ========================================
echo STEP 2: Add All Files to Git
echo ========================================
echo.
git add .
echo [OK] Files added to git
echo.
echo ========================================
echo STEP 3: Create Initial Commit
echo ========================================
echo.
git commit -m "Initial commit: Fraud Detection SaaS"
if %errorlevel% neq 0 (
    echo Please configure git user first:
    echo git config --global user.name "Your Name"
    echo git config --global user.email "your.email@example.com"
    pause
    exit /b 1
)
echo [OK] Commit created
echo.
echo ========================================
echo STEP 4: Create GitHub Repository
echo ========================================
echo.
echo MANUAL ACTION REQUIRED:
echo 1. Go to https://github.com/new
echo 2. Create a new repository (name it: fraud-detection-saas)
echo 3. DO NOT initialize with README or .gitignore
echo 4. Click "Create repository"
echo 5. Copy the repository URL
echo.
echo When ready, paste the GitHub repository URL:
set /p repo_url="Repository URL: "
echo.
echo ========================================
echo STEP 5: Add Remote and Push
echo ========================================
echo.
git remote add origin %repo_url%
git branch -M main
git push -u origin main
if %errorlevel% neq 0 (
    echo Push failed. You may need to authenticate with GitHub.
    echo If using SSH, make sure your SSH key is configured.
    echo If using HTTPS, you may need to use a Personal Access Token.
    pause
    exit /b 1
)
echo [OK] Code pushed to GitHub
echo.
echo ========================================
echo STEP 6: Deploy to Render
echo ========================================
echo.
echo MANUAL ACTION REQUIRED:
echo 1. Go to https://dashboard.render.com/
echo 2. Sign up or log in to Render
echo 3. Click "New +" then "Blueprint"
echo 4. Connect your GitHub account
echo 5. Select the fraud-detection-saas repository
echo 6. Render will automatically detect render.yaml
echo 7. Review the configuration and click "Apply"
echo 8. Wait for deployment to complete (5-10 minutes)
echo.
echo Your services will be available at:
echo - Frontend: https://fraud-detection-frontend.onrender.com
echo - Backend: https://fraud-detection-backend.onrender.com
echo - API Docs: https://fraud-detection-backend.onrender.com/docs
echo.
echo ========================================
echo DEPLOYMENT INSTRUCTIONS COMPLETE
echo ========================================
echo.
echo For detailed troubleshooting, see SAAS_README.md
echo.
pause
