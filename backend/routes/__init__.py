from routes.auth import router as auth_router
from routes.disease import router as disease_router
from routes.yield_prediction import router as yield_router
from routes.dashboard import router as dashboard_router

__all__ = ["auth_router", "disease_router", "yield_router", "dashboard_router"]
