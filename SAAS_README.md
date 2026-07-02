# 🚀 Fraud Detection SaaS - Deployment Guide

Transform your ML fraud detection model into a fully deployable SaaS application.

## 📋 Overview

This SaaS application provides:
- **User Authentication** - JWT-based registration and login
- **Dataset Upload** - Upload transaction data (CSV, XLSX, JSON)
- **Real-time Analysis** - Async fraud detection using your ML models
- **Results Dashboard** - Interactive visualization with SHAP explanations
- **Free Tier** - Deploy on Render's free tier for resume showcase

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI   │────▶│  PostgreSQL │
│  Frontend   │     │   Backend   │     │  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  ML Models  │
                    │ (GraphSAGE  │
                    │  + A3TGCN   │
                    │  + XGBoost) │
                    └─────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async web framework
- **PostgreSQL** - Relational database
- **Redis** - Caching and job queue
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Material-UI** - Component library
- **Recharts** - Data visualization
- **Axios** - HTTP client

### Infrastructure
- **Docker** - Containerization
- **Render** - Cloud hosting (free tier)
- **NGINX** - Reverse proxy

## 📦 Project Structure

```
fraud-detection-main/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── auth.py            # Authentication logic
│   │   └── ml_service.py      # ML model integration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/            # React pages
│   │   ├── components/       # React components
│   │   ├── api/              # API clients
│   │   └── contexts/         # React contexts
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
├── scripts/
│   └── generate_demo_data.py # Demo data generator
├── docker-compose.yml        # Local development
├── render.yaml              # Render deployment config
├── .env.example             # Environment variables template
└── SAAS_README.md           # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Node.js 18+

### Local Development

1. **Clone and navigate to project**
```bash
cd fraud-detection-main
```

2. **Generate demo data**
```bash
python scripts/generate_demo_data.py
```

3. **Start services with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Deploy to Render (Free Tier)

### 1. Prepare Your Code

```bash
# Create a new GitHub repository
git init
git add .
git commit -m "Initial commit: Fraud Detection SaaS"

# Push to GitHub
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy on Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Review the configuration and click "Apply"

### 3. Environment Variables

Render will automatically set:
- `DATABASE_URL` (from PostgreSQL service)
- `REDIS_URL` (from Redis service)
- `SECRET_KEY` (auto-generated)

### 4. Access Your App

After deployment (~5-10 minutes):
- Frontend: `https://fraud-detection-frontend.onrender.com`
- Backend: `https://fraud-detection-backend.onrender.com`
- API Docs: `https://fraud-detection-backend.onrender.com/docs`

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Datasets
- `POST /datasets` - Upload dataset
- `GET /datasets` - List user datasets
- `GET /datasets/{id}` - Get dataset details

### Analyses
- `POST /analyses` - Create analysis
- `GET /analyses` - List user analyses
- `GET /analyses/{id}` - Get analysis results

### Predictions
- `POST /predict` - Single transaction prediction

### Health
- `GET /health` - Health check

## 🧪 Testing the Application

### 1. Register a User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 3. Upload Dataset
```bash
curl -X POST http://localhost:8000/datasets \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@demo_transactions.csv" \
  -F "name=Demo Dataset"
```

### 4. Create Analysis
```bash
curl -X POST http://localhost:8000/analyses \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1}'
```

## 🎨 Features Showcase

### For Your Resume

**Full-Stack Development:**
- Built RESTful API with FastAPI
- Developed React frontend with TypeScript
- Implemented JWT authentication
- Created responsive UI with Material-UI

**ML Engineering:**
- Integrated ML models into production system
- Implemented batch processing pipeline
- Added SHAP explainability
- Created async job processing

**DevOps:**
- Containerized application with Docker
- Configured production deployment on Render
- Set up PostgreSQL and Redis
- Implemented environment variable management

**Data Visualization:**
- Interactive charts with Recharts
- Real-time analysis results
- Feature importance plots
- Fraud score distribution

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `SECRET_KEY` | JWT secret key | - |
| `DEBUG` | Debug mode | `true` |
| `MODEL_PATH` | Path to ML models | `../artifacts` |
| `MAX_DATASET_SIZE` | Max rows for free tier | `100000` |
| `MAX_UPLOAD_SIZE` | Max file size in bytes | `10485760` |
| `CORS_ORIGINS` | Allowed CORS origins | `localhost:3000` |

## 📈 Scaling Considerations

For production beyond the free tier:

1. **Database**: Upgrade to managed PostgreSQL with backups
2. **Caching**: Add Redis Cluster for high availability
3. **Storage**: Use S3-compatible storage for datasets
4. **ML**: Deploy models as separate microservices
5. **Monitoring**: Add application monitoring (Sentry, DataDog)
6. **CDN**: Use CloudFront for static assets

## 🐛 Troubleshooting

### Common Issues

**Database connection fails:**
- Check PostgreSQL is running: `docker-compose ps postgres`
- Verify DATABASE_URL in .env

**Frontend can't connect to backend:**
- Check CORS_ORIGINS includes your frontend URL
- Verify backend is running on port 8000

**ML model loading fails:**
- Ensure artifacts directory exists with trained models
- Check MODEL_PATH is correct
- For demo, the system will use dummy predictions

**Deployment fails on Render:**
- Check render.yaml syntax
- Verify all services are defined correctly
- Check Render logs for specific errors

## 📝 Next Steps for Production

1. **Add proper error handling and logging**
2. **Implement rate limiting**
3. **Add email verification**
4. **Set up monitoring and alerting**
5. **Add backup/recovery procedures**
6. **Implement payment processing (Stripe)**
7. **Add admin dashboard**
8. **Create API documentation**
9. **Set up CI/CD pipeline**
10. **Add comprehensive tests**

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Render Documentation](https://render.com/docs)
- [Docker Documentation](https://docs.docker.com/)

## 📄 License

This project extends the original fraud detection ML system with SaaS capabilities.

## 🤝 Contributing

This is a demo/resume project. Feel free to fork and customize for your needs!

---

**Built for showcasing full-stack ML engineering skills.** 🚀
