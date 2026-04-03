# AgroVision AI 🌿

> **Smart Crop Intelligence Platform** — AI-powered disease detection and yield prediction for farmers and agronomists.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)](https://tensorflow.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.x-red)](https://xgboost.ai/)

---

## ✨ Features

- 🔍 **Disease Detection**: Upload a leaf photo → instant AI diagnosis with treatment plan
- 📈 **Yield Prediction**: Ensemble model (XGBoost + DNN + Random Forest) for accurate forecasts
- 📊 **Dashboard**: Real-time charts, statistics, and recent activity
- 📅 **History**: Browse and delete past detections / predictions
- 👤 **Profile**: Manage account, change password
- 🔒 **Auth**: JWT-based authentication (register + login)
- 🟡 **Demo Mode**: Works fully without trained models (realistic mock predictions)

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, Tailwind CSS, Framer Motion |
| Backend | FastAPI, SQLAlchemy, SQLite |
| ML | TensorFlow/Keras (EfficientNetB3), XGBoost, scikit-learn |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Charts | Recharts |
| DevOps | Docker, Docker Compose |

---

## 🚀 Quick Start

### Option 1: Docker (recommended)

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd 6_sgp

# 2. Start everything
docker-compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Option 2: Manual Development Setup

#### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
copy .env.example .env

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend API docs: `http://localhost:8000/docs`

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy and configure
copy .env.example .env

# Start dev server
npm run dev
```

Frontend: `http://localhost:5173`

---

## 🤖 Training ML Models (Optional)

The app works in **demo mode** without trained models. To train real models:

### 1. Set up Kaggle credentials

```bash
# Get API key from https://www.kaggle.com/account
set KAGGLE_USERNAME=your_username
set KAGGLE_KEY=your_api_key
```

### 2. Download datasets

```bash
cd backend
python ml/download_datasets.py
```

### 3. Process data

```bash
python ml/data_pipeline.py
```

### 4. Train models

```bash
# Disease detection (EfficientNetB3, ~30 min with GPU)
python ml/train_disease_model.py

# Yield prediction (XGBoost + DNN ensemble, ~10 min)
python ml/train_yield_model.py
```

Trained models are saved to `backend/ml/saved_models/`.

---

## 📁 Project Structure

```
6_sgp/
├── backend/
│   ├── ml/
│   │   ├── disease_predictor.py   # Disease inference (+ demo mode)
│   │   ├── yield_predictor.py     # Yield inference (+ demo mode)
│   │   ├── model_loader.py        # Lazy model loading
│   │   ├── data_pipeline.py       # Dataset processing
│   │   ├── download_datasets.py   # Kaggle downloader
│   │   ├── train_disease_model.py # Training scripts
│   │   └── train_yield_model.py
│   ├── models/                    # SQLAlchemy ORM models
│   ├── routes/                    # FastAPI routers
│   ├── schemas/                   # Pydantic schemas
│   ├── utils/                     # Auth, image processing, responses
│   ├── main.py                    # FastAPI application entry
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/                   # Axios API modules
│       ├── components/            # Reusable UI components
│       ├── context/               # React Context (Auth)
│       ├── pages/                 # 8 app pages
│       └── utils/                 # Helpers & constants
├── docker-compose.yml
└── README.md
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, get JWT |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/disease/detect` | Upload image, get disease |
| GET | `/api/disease/history` | Disease detection history |
| POST | `/api/yield/predict` | Predict crop yield |
| GET | `/api/yield/history` | Yield prediction history |
| GET | `/api/dashboard/stats` | Dashboard statistics |

Interactive docs: `http://localhost:8000/docs`

---

## 🌱 Demo Mode

When trained models are not found, AgroVision runs in **demo mode**:
- Disease detection returns realistic mock predictions based on a database of 38 crop diseases
- Yield prediction generates plausible estimates using agricultural parameters
- All endpoints are fully functional for testing and presentation

---

## 📄 License

MIT License — Free to use, modify, and distribute.
