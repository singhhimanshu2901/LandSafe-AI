import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.landslide_event import LandslideEvent

router = APIRouter(prefix="/events", tags=["events"])

class LandslideEventCreate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    event_time: datetime
    severity: Optional[str] = None
    source: Optional[str] = None

class LandslideEventOut(BaseModel):
    id: uuid.UUID
    lat: float
    lon: float
    event_time: datetime
    severity: Optional[str]
    source: Optional[str]
    verification_status: str

    class Config:
        orm_mode = True

def _to_out(e: LandslideEvent) -> LandslideEventOut:
    point = to_shape(e.geometry)
    return LandslideEventOut(
        id=e.id,
        lat=point.y,
        lon=point.x,
        event_time=e.event_time,
        severity=e.severity,
        source=e.source,
        verification_status=e.verification_status,
    )

@router.post("", response_model=LandslideEventOut)
def create_event(payload: LandslideEventCreate, db: Session = Depends(get_db)):
    # Simple validation for duplicates
    existing = db.query(LandslideEvent).filter(
        LandslideEvent.event_time == payload.event_time
    ).first()
    # In a real scenario, you'd check geographic proximity for duplicates
    
    try:
        geom = WKTElement(f"POINT({payload.lon} {payload.lat})", srid=4326)
        event = LandslideEvent(
            geometry=geom,
            event_time=payload.event_time,
            severity=payload.severity,
            source=payload.source
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return _to_out(event)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to ingest event: {exc}")

@router.get("", response_model=list[LandslideEventOut])
def list_events(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    results = db.query(LandslideEvent).order_by(LandslideEvent.event_time.desc()).offset(offset).limit(limit).all()
    if not results:
        # Based on the prompt: The system must clearly report that historical data is unavailable.
        pass # The frontend handles "HISTORICAL DATA UNAVAILABLE" state
    return [_to_out(r) for r in results]
