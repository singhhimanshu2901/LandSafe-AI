from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

@router.get("/{location_id}")
def get_location_intelligence(location_id: uuid.UUID, db: Session = Depends(get_db)):
    # Get location
    loc = db.execute(text("SELECT id, ST_X(geometry::geometry) as lon, ST_Y(geometry::geometry) as lat, elevation, slope, district, village FROM locations WHERE id = :id"), {"id": str(location_id)}).fetchone()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
        
    # Get latest risk
    risk = db.execute(text("SELECT level, probability, timestamp, details FROM risk_predictions WHERE location_id = :id ORDER BY timestamp DESC LIMIT 1"), {"id": str(location_id)}).fetchone()
    
    # Get latest weather
    weather = db.execute(text("SELECT rainfall, temperature, humidity, timestamp FROM weather_observations WHERE location_id = :id ORDER BY timestamp DESC LIMIT 1"), {"id": str(location_id)}).fetchone()
    
    # Get sensor readings within distance (e.g., closest)
    # Just checking if any sensor reading exists for now.
    sensors_exist = db.execute(text("SELECT COUNT(*) FROM sensor_readings")).scalar() > 0
    
    # Get historical landslide events within distance
    historical_exist = db.execute(text("SELECT COUNT(*) FROM landslide_events")).scalar() > 0
    
    now = datetime.utcnow()
    
    # Calculate weather freshness
    weather_status = "UNAVAILABLE"
    if weather and weather.timestamp:
        diff = (now - weather.timestamp).total_seconds() / 3600
        if diff <= 2:
            weather_status = "LIVE"
        elif diff <= 24:
            weather_status = "PARTIAL"
        else:
            weather_status = "STALE"
            
    # Risk calculation
    risk_level = risk.level if risk else "UNAVAILABLE"
    probability = risk.probability if risk else None
    risk_timestamp = risk.timestamp if risk else None
    details = risk.details if risk and risk.details else {}
    
    # Recommended Action
    rec = "Continue normal monitoring."
    if risk_level == "MEDIUM":
        rec = "Increase monitoring frequency. Review local conditions."
    elif risk_level == "HIGH":
        rec = "Issue warning. Avoid vulnerable slopes/roads. Increase field monitoring."
    elif risk_level == "CRITICAL":
        rec = "Follow emergency procedures. Avoid affected areas. Escalate to authorities."
    
    return {
        "location_id": str(loc.id),
        "lat": loc.lat,
        "lon": loc.lon,
        "elevation": loc.elevation,
        "slope": loc.slope,
        "weather": {
            "status": weather_status,
            "rainfall": weather.rainfall if weather else None,
            "temperature": weather.temperature if weather else None,
            "humidity": weather.humidity if weather else None,
            "timestamp": weather.timestamp if weather else None,
        },
        "risk": {
            "level": risk_level,
            "probability": probability,
            "timestamp": risk_timestamp
        },
        "sensors": {
            "status": "LIVE" if sensors_exist else "SENSOR DATA UNAVAILABLE"
        },
        "historical": {
            "status": "AVAILABLE" if historical_exist else "HISTORICAL DATA UNAVAILABLE"
        },
        "ai_explanation": details,
        "recommended_action": rec
    }
