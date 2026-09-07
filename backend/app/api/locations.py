import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationOut

router = APIRouter(prefix="/locations", tags=["locations"])


def _to_out(loc: Location) -> LocationOut:
    point = to_shape(loc.geometry)
    return LocationOut(
        id=loc.id,
        lat=point.y,
        lon=point.x,
        district=loc.district,
        village=loc.village,
        elevation=loc.elevation,
        slope=loc.slope,
        created_at=loc.created_at,
    )


@router.post("", response_model=LocationOut)
def create_location(payload: LocationCreate, db: Session = Depends(get_db)):
    try:
        geom = WKTElement(f"POINT({payload.lon} {payload.lat})", srid=4326)
        loc = Location(
            geometry=geom,
            district=payload.district,
            village=payload.village,
            elevation=payload.elevation,
            slope=payload.slope,
        )
        db.add(loc)
        db.commit()
        db.refresh(loc)
        return _to_out(loc)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create location: {e}")


@router.get("", response_model=list[LocationOut])
def list_locations(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    locs = db.query(Location).offset(offset).limit(limit).all()
    return [_to_out(l) for l in locs]


@router.get("/{location_id}", response_model=LocationOut)
def get_location(location_id: uuid.UUID, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return _to_out(loc)
