@echo off
echo 🚀 Starting Fraud Detection SaaS locally...

REM Generate demo data
echo 📊 Generating demo data...
python scripts/generate_demo_data.py

REM Start Docker services
echo 🐳 Starting Docker services...
docker-compose up -d

echo ✅ Services started!
echo.
echo 📱 Frontend: http://localhost
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo To stop services, run: docker-compose down
pause
