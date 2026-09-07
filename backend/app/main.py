from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from app.api import locations, weather, sensors, risk, gis, reports, alerts, auth, events, intelligence, analytics
from app.core.config import settings
from app.db.session import get_db

app = FastAPI(title="Landsafe AI API")

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")] if settings.ALLOWED_ORIGINS else []
if settings.ENV == "development":
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1 = APIRouter(prefix="/api/v1")


@api_v1.get("/health")
def health(db: Session = Depends(get_db)):
    health_status = {"status": "ok", "database": "unknown", "ml_model": "unknown"}
    
    # Check Database
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception:
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"
        
    # Check ML Model
    try:
        model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models")
        if os.path.exists(model_dir) and any(f.endswith(".joblib") for f in os.listdir(model_dir)):
            health_status["ml_model"] = "available"
        else:
            health_status["ml_model"] = "missing"
            health_status["status"] = "degraded"
    except Exception:
        pass

    return health_status


api_v1.include_router(locations.router)
api_v1.include_router(weather.router)
api_v1.include_router(sensors.router)
api_v1.include_router(risk.router)
api_v1.include_router(gis.router)
api_v1.include_router(reports.router)
api_v1.include_router(alerts.router)
api_v1.include_router(auth.router)
api_v1.include_router(events.router)
api_v1.include_router(intelligence.router)
api_v1.include_router(analytics.router)

app.include_router(api_v1)
