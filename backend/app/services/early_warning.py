import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.alert import Alert
from app.models.risk_prediction import RiskPrediction

logger = logging.getLogger(__name__)

LEVEL_MAP = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3
}

def evaluate_and_generate_alert(db: Session, risk_prediction: RiskPrediction, location_id: str):
    """
    Automatic Early Warning Engine.
    Evaluates the fresh risk prediction and creates an alert if necessary,
    handling escalation and duplicate prevention.
    """
    current_level_str = risk_prediction.level.upper()
    current_level_val = LEVEL_MAP.get(current_level_str, 0)
    
    # Find the most recent alert for this location
    latest_alert_query = text("""
        SELECT a.id, a.template, a.sent_at, rp.level as alert_level
        FROM alerts a
        JOIN risk_predictions rp ON a.risk_prediction_id = rp.id
        WHERE rp.location_id = :loc_id
        ORDER BY a.sent_at DESC
        LIMIT 1
    """)
    
    latest_alert = db.execute(latest_alert_query, {"loc_id": location_id}).fetchone()
    
    # Determine the "active" risk level based on the last alert
    last_active_level_val = 0
    if latest_alert:
        if "Resolved" in latest_alert.template or "returned to normal" in latest_alert.template:
            last_active_level_val = 0
        else:
            last_active_level_str = (latest_alert.alert_level or "").upper()
            last_active_level_val = LEVEL_MAP.get(last_active_level_str, 0)
            
    # Decision Logic
    action = None
    template_msg = None
    
    if current_level_val == 0:
        # LOW
        if last_active_level_val >= 2: # Previously HIGH or CRITICAL
            action = "RESOLVE"
            template_msg = f"Resolved: Landslide risk at {location_id} has returned to normal (LOW)."
    
    elif current_level_val == 1:
        # MEDIUM
        if last_active_level_val == 0:
            action = "ADVISORY"
            template_msg = f"Advisory: Medium landslide risk detected at {location_id}. Score: {risk_prediction.score:.2f}."
        elif last_active_level_val >= 2:
            action = "RESOLVE"
            template_msg = f"Downgraded: Landslide risk at {location_id} has decreased to MEDIUM."
            
    elif current_level_val == 2:
        # HIGH
        if last_active_level_val < 2:
            action = "WARNING"
            template_msg = f"Warning: High landslide risk detected at {location_id}. Score: {risk_prediction.score:.2f}."
        # If it was already HIGH or CRITICAL, we don't duplicate or downgrade CRITICAL to HIGH via alerts unless we want to.
        # Let's just suppress duplicate HIGH.
        
    elif current_level_val == 3:
        # CRITICAL
        if last_active_level_val < 3:
            action = "EMERGENCY"
            template_msg = f"Emergency: Critical landslide risk detected at {location_id}. Immediate precautionary action is recommended. Score: {risk_prediction.score:.2f}."

    if action and template_msg:
        alert = Alert(
            id=uuid.uuid4(),
            risk_prediction_id=risk_prediction.id,
            audience="public",
            channel="dashboard",
            template=template_msg,
            sent_at=datetime.utcnow(),
            delivery_status="sent"
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        logger.info(f"Automatic Alert Engine: Created {action} alert for location {location_id}. Alert ID: {alert.id}")
        return alert
        
    logger.info(f"Automatic Alert Engine: No alert generated for location {location_id}. Current Level: {current_level_str}. Last Active: {last_active_level_val}.")
    return None
