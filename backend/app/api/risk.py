import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.risk_prediction import RiskPrediction
from app.schemas.risk import RiskPredictionOut

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("", response_model=list[RiskPredictionOut])
def list_risk(
    level: str | None = None,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(RiskPrediction)
    if level:
        q = q.filter(RiskPrediction.level == level)
    return q.order_by(RiskPrediction.timestamp.desc()).offset(offset).limit(limit).all()


@router.get("/{location_id}", response_model=RiskPredictionOut)
def get_location_risk(location_id: uuid.UUID, db: Session = Depends(get_db)):
    pred = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.location_id == location_id)
        .order_by(RiskPrediction.timestamp.desc())
        .first()
    )
    if not pred:
        raise HTTPException(status_code=404, detail="No risk prediction found for this location")
    return pred
