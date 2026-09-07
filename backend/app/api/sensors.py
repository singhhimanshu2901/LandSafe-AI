from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models.sensor_reading import SensorReading
from app.schemas.sensor import SensorReadingCreate, SensorReadingOut

router = APIRouter(prefix="/sensors", tags=["sensors"])


def _to_out(s: SensorReading) -> SensorReadingOut:
    point = to_shape(s.geometry)
    return SensorReadingOut(
        id=s.id,
        sensor_id=s.sensor_id,
        lat=point.y,
        lon=point.x,
        timestamp=s.timestamp,
        soil_moisture=s.soil_moisture,
        battery=s.battery,
        quality=s.quality,
    )


@router.post("", response_model=SensorReadingOut)
def ingest_sensor_reading(payload: SensorReadingCreate, db: Session = Depends(get_db)):
    if payload.soil_moisture is not None and not (0 <= payload.soil_moisture <= 100):
        raise HTTPException(status_code=400, detail="soil_moisture must be between 0 and 100")
        
    # Check for duplicates (same sensor_id and timestamp)
    ts = payload.timestamp or datetime.utcnow()
    existing = db.query(SensorReading).filter(
        SensorReading.sensor_id == payload.sensor_id,
        SensorReading.timestamp == ts
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Duplicate sensor reading for this timestamp")
        
    try:
        geom = WKTElement(f"POINT({payload.lon} {payload.lat})", srid=4326)
        reading = SensorReading(
            sensor_id=payload.sensor_id,
            geometry=geom,
            timestamp=payload.timestamp or datetime.utcnow(),
            soil_moisture=payload.soil_moisture,
            battery=payload.battery,
            quality=payload.quality,
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return _to_out(reading)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to ingest sensor reading: {e}")


@router.get("", response_model=list[SensorReadingOut])
def list_sensor_readings(
    sensor_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(SensorReading)
    if sensor_id:
        q = q.filter(SensorReading.sensor_id == sensor_id)
    if date_from:
        q = q.filter(SensorReading.timestamp >= date_from)
    if date_to:
        q = q.filter(SensorReading.timestamp <= date_to)
    results = q.offset(offset).limit(limit).all()
    return [_to_out(r) for r in results]
