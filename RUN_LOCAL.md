# 🚀 Running the Project Locally

Since Docker isn't available, we'll run the backend and frontend separately.

## 📋 Prerequisites

- Python 3.9+ 
- Node.js 18+
- pip (Python package manager)
- npm (Node package manager)

## 🔧 Step 1: Install Backend Dependencies

Open a new terminal/command prompt and run:

```bash
cd backend
pip install -r requirements.txt
```

**Or use the provided script:**
```bash
run_backend.bat
```

## 🔧 Step 2: Start Backend Server

Keep the terminal open and start the FastAPI server:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend will be available at:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 🔧 Step 3: Install Frontend Dependencies

Open a **new** terminal/command prompt (keep the backend running) and run:

```bash
cd frontend
npm install
```

## 🔧 Step 4: Start Frontend Development Server

In the same terminal (after npm install completes):

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## 🎯 Step 5: Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## 🧪 Testing the Application

### 1. Register a New User
- Click "Sign Up" on the login page
- Enter email, username, and password
- Click "Sign Up" button

### 2. Upload Dataset
- Go to Dashboard
- Click "Upload New Dataset"
- Select the `demo_transactions.csv` file (generated earlier)
- Enter a name for the dataset
- Click "Upload and Analyze"

### 3. View Results
- The analysis will start automatically
- You'll be redirected to the results page
- Watch the analysis progress (polling every 3 seconds)
- View fraud statistics, charts, and SHAP explanations

## 🐛 Troubleshooting

### Backend Issues

**Import errors:**
```bash
cd backend
pip install -r requirements.txt
```

**Database errors:**
- The backend uses SQLite by default (no PostgreSQL needed)
- Database file will be created automatically: `backend/fraud_detection.db`

**Port already in use:**
```bash
# Change the port in the command:
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Issues

**npm install fails:**
```bash
cd frontend
npm cache clean --force
npm install
```

**Port already in use:**
```bash
# Vite will automatically find an available port
# Or specify a different port:
npm run dev -- --port 3000
```

**CORS errors:**
- Ensure backend is running on port 8000
- Check that `CORS_ORIGINS` in `backend/.env` includes your frontend URL

## 📊 Quick Test with API

You can also test the backend directly using the API docs:

1. Open http://localhost:8000/docs in your browser
2. Try the health check endpoint
3. Register a new user using the `/auth/register` endpoint
4. Login using the `/auth/login` endpoint
5. Use the token to test other endpoints

## 🛑 Stopping the Servers

To stop the servers:
- Press `Ctrl+C` in each terminal
- Close the terminal windows

## 🎓 What to Test

1. **User Registration & Login**
   - Create a new account
   - Login successfully
   - Access protected routes

2. **Dataset Upload**
   - Upload CSV file
   - See file validation
   - Check dataset appears in list

3. **Analysis Processing**
   - Create analysis from dataset
   - Watch processing status
   - View completed results

4. **Results Visualization**
   - Check statistics display
   - Verify charts render correctly
   - Review SHAP explanations

5. **Error Handling**
   - Try uploading invalid file
   - Test with very large files
   - Check error messages

## 📝 Notes

- The backend uses **dummy predictions** by default (since ML models aren't trained)
- This is perfect for testing the UI and API flow
- For production use, you'd train the models and place them in the `artifacts/` directory
- SQLite database is used for simplicity (PostgreSQL recommended for production)

Good luck with your testing! 🚀
