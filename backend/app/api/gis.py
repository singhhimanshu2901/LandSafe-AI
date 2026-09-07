"""
Phase 9: GIS spatial intelligence - find exposed roads, villages, infrastructure
within a risk zone / radius of a location.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.models.location import Location
from app.models.infrastructure import Infrastructure
from app.models.road import Road

router = APIRouter(prefix="/gis", tags=["gis"])


@router.get("/infrastructure/nearby")
def infrastructure_nearby(
    location_id: uuid.UUID,
    radius_km: float = Query(5.0, gt=0, le=100),
    db: Session = Depends(get_db),
):
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    radius_m = radius_km * 1000
    q = text(
        """
        SELECT id, type, name, importance,
               ST_Y(geometry::geometry) as lat, ST_X(geometry::geometry) as lon,
               ST_Distance(geometry::geography, (SELECT geometry::geography FROM locations WHERE id = :loc_id)) as distance_m
        FROM infrastructure
        WHERE ST_DWithin(geometry::geography, (SELECT geometry::geography FROM locations WHERE id = :loc_id), :radius_m)
        ORDER BY distance_m ASC
        """
    )
    rows = db.execute(q, {"loc_id": str(location_id), "radius_m": radius_m}).mappings().all()
    return {"location_id": str(location_id), "radius_km": radius_km, "results": [dict(r) for r in rows]}


@router.get("/roads/nearby")
def roads_nearby(
    location_id: uuid.UUID,
    radius_km: float = Query(5.0, gt=0, le=100),
    db: Session = Depends(get_db),
):
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    radius_m = radius_km * 1000
    q = text(
        """
        SELECT id, road_type, status,
               ST_Distance(geometry::geography, (SELECT geometry::geography FROM locations WHERE id = :loc_id)) as distance_m
        FROM roads
        WHERE ST_DWithin(geometry::geography, (SELECT geometry::geography FROM locations WHERE id = :loc_id), :radius_m)
        ORDER BY distance_m ASC
        """
    )
    rows = db.execute(q, {"loc_id": str(location_id), "radius_m": radius_m}).mappings().all()
    return {"location_id": str(location_id), "radius_km": radius_km, "results": [dict(r) for r in rows]}
