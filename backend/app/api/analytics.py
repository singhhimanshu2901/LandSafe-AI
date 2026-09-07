from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/")
def get_analytics(db: Session = Depends(get_db)):
    # 1. Risk distribution (count of latest predictions per level)
    risk_dist = db.execute(text("""
        WITH LatestPreds AS (
            SELECT location_id, level, ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY timestamp DESC) as rn
            FROM risk_predictions
        )
        SELECT level, COUNT(*) as count FROM LatestPreds WHERE rn = 1 GROUP BY level
    """)).fetchall()
    
    # 2. Warning count
    warning_count = db.execute(text("SELECT COUNT(*) FROM alerts")).scalar()
    
    # 3. Data quality distribution
    # Simplified version based on recent weather updates
    stale_count = db.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT location_id, MAX(timestamp) as max_ts FROM weather_observations GROUP BY location_id
        ) sub WHERE max_ts < NOW() - INTERVAL '24 hours'
    """)).scalar()
    
    total_locations = db.execute(text("SELECT COUNT(*) FROM locations")).scalar()
    
    # 4. Rainfall -> Risk Analysis (raw data for chart)
    # Get last 100 predictions with their corresponding rainfall from weather table
    # Since they are inserted together, we can join them loosely by location and nearest time
    rain_risk_raw = db.execute(text("""
        SELECT r.probability, w.rainfall, r.timestamp
        FROM risk_predictions r
        JOIN weather_observations w ON r.location_id = w.location_id
        AND w.timestamp >= r.timestamp - INTERVAL '1 hour'
        AND w.timestamp <= r.timestamp
        ORDER BY r.timestamp DESC LIMIT 100
    """)).fetchall()
    
    rain_risk_data = [{"probability": r[0], "rainfall_1h": r[1], "timestamp": r[2]} for r in rain_risk_raw]

    return {
        "risk_distribution": [{"level": r[0], "count": r[1]} for r in risk_dist],
        "warning_count": warning_count,
        "data_quality": {
            "stale": stale_count,
            "live_or_partial": total_locations - stale_count
        },
        "rainfall_risk": rain_risk_data
    }
