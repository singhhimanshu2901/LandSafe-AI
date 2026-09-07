import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.location import Location
from app.models.weather_observation import WeatherObservation
from app.schemas.weather import WeatherObservationCreate, WeatherObservationOut

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post("", response_model=WeatherObservationOut)
def ingest_weather(payload: WeatherObservationCreate, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == payload.location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="location_id does not exist")
    try:
        obs = WeatherObservation(
            location_id=payload.location_id,
            timestamp=payload.timestamp or datetime.utcnow(),
            rainfall=payload.rainfall,
            temperature=payload.temperature,
            humidity=payload.humidity,
            source=payload.source,
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)
        return obs
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to ingest weather: {e}")


@router.get("", response_model=list[WeatherObservationOut])
def list_weather(
    location_id: Optional[uuid.UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(WeatherObservation)
    if location_id:
        q = q.filter(WeatherObservation.location_id == location_id)
    if date_from:
        q = q.filter(WeatherObservation.timestamp >= date_from)
    if date_to:
        q = q.filter(WeatherObservation.timestamp <= date_to)
    return q.offset(offset).limit(limit).all()
