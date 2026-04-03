import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from database import engine, Base
import models  # Import all models to register them

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    os.makedirs(os.getenv("UPLOAD_DIR", "uploads"), exist_ok=True)
    print("[AgroVision] Database tables created.")
    from ml.model_loader import load_all_models
    load_all_models()
    yield
    # Shutdown
    print("[AgroVision] Server shutting down.")


app = FastAPI(
    title="AgroVision AI API",
    description="Smart Agriculture Platform - Crop Disease Detection & Yield Prediction",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
upload_dir = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Register routes
from routes.auth import router as auth_router
from routes.disease import router as disease_router
from routes.yield_prediction import router as yield_router
from routes.dashboard import router as dashboard_router

app.include_router(auth_router)
app.include_router(disease_router)
app.include_router(yield_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "name": "AgroVision AI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
