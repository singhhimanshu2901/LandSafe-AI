"""
Phase 12: Alerting and early warning engine.

Converts risk levels + rules into graded alerts (Advisory/Watch/Warning/Emergency)
and dispatches via configured channel (stubbed for prototype - logs instead of
real SMS/push).
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.alert import Alert
from app.models.risk_prediction import RiskPrediction
from app.schemas.alert import AlertCreate, AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])

LEVEL_TO_ALERT = {
    "Very Low": None,
    "Low": None,
    "Moderate": "Advisory",
    "High": "Watch",
    "Critical": "Emergency",
}


def _dispatch(channel: str, template: str):
    """Stub dispatcher - replace with real SMS/push provider integration."""
    print(f"[ALERT DISPATCH] channel={channel} message={template}")
    return "sent"


@router.post("", response_model=AlertOut)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    try:
        status = _dispatch(payload.channel, payload.template)
        alert = Alert(
            risk_prediction_id=payload.risk_prediction_id,
            audience=payload.audience,
            channel=payload.channel,
            template=payload.template,
            sent_at=datetime.utcnow(),
            delivery_status=status,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {e}")


@router.post("/test")
def test_alert(channel: str, template: str = "This is a Landsafe AI test notification."):
    status = _dispatch(channel, template)
    return {"channel": channel, "template": template, "status": status}


@router.get("", response_model=list[AlertOut])
def list_alerts(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return db.query(Alert).order_by(Alert.sent_at.desc()).offset(offset).limit(limit).all()


@router.post("/evaluate/{risk_prediction_id}")
def evaluate_and_alert(risk_prediction_id: str, db: Session = Depends(get_db)):
    """Given a risk_prediction, decide alert level and auto-create an alert if warranted."""
    pred = db.query(RiskPrediction).filter(RiskPrediction.id == risk_prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Risk prediction not found")

    alert_level = LEVEL_TO_ALERT.get(pred.level)
    if not alert_level:
        return {"alert_created": False, "reason": f"level '{pred.level}' does not warrant an alert"}

    template = f"{alert_level}: Landslide risk level '{pred.level}' detected (score={pred.score})."
    status = _dispatch("dashboard", template)
    alert = Alert(
        risk_prediction_id=pred.id, audience="district_officials", channel="dashboard",
        template=template, sent_at=datetime.utcnow(), delivery_status=status,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"alert_created": True, "alert_id": str(alert.id), "level": alert_level}
