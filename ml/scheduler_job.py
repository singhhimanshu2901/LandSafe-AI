import os
import sys
import time
import schedule
from datetime import datetime, timedelta
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.feature_engineering.pipeline import build_feature_table
from ml.feature_engineering.config import get_db_url
from ml.inference import RiskInferencePipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(get_db_url()) if os.getenv("DATABASE_URL") else None
Session = sessionmaker(bind=engine) if engine else None

interval_minutes = int(os.getenv("PREDICTION_INTERVAL_MINUTES", "60"))

def run_job():
    print(f"[{datetime.utcnow()}] Starting inference job...")
    try:
        pipeline = RiskInferencePipeline()
        ref_time = datetime.utcnow()
        features_df = build_feature_table(ref_time)
        
        if features_df.empty:
            print("No locations to predict.")
            return

        with engine.begin() as conn:
            for _, row in features_df.iterrows():
                try:
                    loc_id = str(row["location_id"])
                    feat_dict = row.to_dict()
                    pred = pipeline.predict(feat_dict)
                    
                    pred_id = str(uuid.uuid4())
                    
                    import json
                    details_json = json.dumps(pred.get("details", {}))
                    
                    query = text("""
                        INSERT INTO risk_predictions (id, location_id, timestamp, probability, score, level, model_version, details)
                        VALUES (:id, :loc_id, :ts, :prob, :prob, :level, :version, :details::jsonb)
                    """)
                    conn.execute(query, {
                        "id": pred_id,
                        "loc_id": loc_id,
                        "ts": pred["timestamp"],
                        "prob": pred["probability"],
                        "level": pred["level"],
                        "version": pred["model_version"],
                        "details": details_json
                    })
                    
                    # Early Warning System Improvement
                    # Consider risk level, probability, and rapid rainfall increase
                    is_high_risk = pred["level"] in ("HIGH", "CRITICAL")
                    rapid_rainfall = feat_dict.get("rainfall_1h", 0) > 15.0 or feat_dict.get("rainfall_intensity", 0) > 5.0
                    
                    if is_high_risk or rapid_rainfall:
                        # check if previous alert was sent recently to prevent duplicates
                        prev_alert = conn.execute(text("""
                            SELECT sent_at FROM alerts 
                            WHERE risk_prediction_id IN (
                                SELECT id FROM risk_predictions WHERE location_id = :loc_id
                            ) 
                            ORDER BY sent_at DESC LIMIT 1
                        """), {"loc_id": loc_id}).scalar()
                        
                        # Only alert if no alert in the last 2 hours
                        if not prev_alert or (datetime.utcnow() - prev_alert).total_seconds() > 7200:
                            alert_id = str(uuid.uuid4())
                            reason = f"{pred['level']} risk (prob {pred['probability']:.2f})." if is_high_risk else "Rapid rainfall increase detected."
                            template_msg = f"Alert: {reason} Location {loc_id}. Action: Evacuate/Secure area."
                            conn.execute(text("""
                                INSERT INTO alerts (id, risk_prediction_id, audience, channel, template, sent_at, delivery_status)
                                VALUES (:id, :risk_id, 'public', 'sms', :tmpl, :ts, 'sent')
                            """), {
                                "id": alert_id,
                                "risk_id": pred_id,
                                "tmpl": template_msg,
                                "ts": datetime.utcnow()
                            })
                            print(f"Generated alert {alert_id} for location {loc_id}")
                except Exception as e:
                    print(f"Error predicting for location {row.get('location_id')}: {e}")
                    
        print(f"[{datetime.utcnow()}] Successfully completed inference job.")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Inference job failed: {e}")

import requests
from datetime import timedelta

weather_interval_minutes = int(os.getenv("WEATHER_INTERVAL_MINUTES", "120"))

def run_weather_job():
    print(f"[{datetime.utcnow()}] Starting weather ingestion job...")
    try:
        with engine.begin() as conn:
            print("Fetching locations...")
            locations = conn.execute(text("SELECT id, ST_X(geometry::geometry) as lon, ST_Y(geometry::geometry) as lat FROM locations")).fetchall()
            print(f"Found {len(locations)} locations.")
            for loc in locations:
                loc_id = str(loc.id)
                lat, lon = loc.lat, loc.lon
                
                # Get max timestamp for this location
                max_ts = conn.execute(text("SELECT MAX(timestamp) FROM weather_observations WHERE location_id = :loc_id"), {"loc_id": loc_id}).scalar()
                print(f"Max timestamp for {loc_id}: {max_ts}")
                
                try:
                    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&past_days=7&hourly=precipitation,temperature_2m,relative_humidity_2m"
                    print(f"Requesting weather for {loc_id}...")
                    try:
                        res = requests.get(url, timeout=10)
                    except requests.exceptions.SSLError as e:
                        print(f"SSL ERROR: Cannot fetch weather due to local certificate configuration. Ensure valid CA root certificates are installed for Open-Meteo API. Exception: {e}")
                        continue
                    print(f"Received weather for {loc_id}, status={res.status_code}")
                    if res.status_code != 200:
                        print(f"Failed to fetch weather for {loc_id}: {res.status_code} {res.text}")
                        continue
                        
                    data = res.json()
                    hourly = data.get("hourly", {})
                    times = hourly.get("time", [])
                    precip = hourly.get("precipitation", [])
                    temp = hourly.get("temperature_2m", [])
                    humidity = hourly.get("relative_humidity_2m", [])
                    
                    inserted = 0
                    batch_params = []
                    for t_str, p, tp, h in zip(times, precip, temp, humidity):
                        dt = datetime.fromisoformat(t_str)
                        if max_ts and dt <= max_ts:
                            continue
                        batch_params.append({
                            "id": str(uuid.uuid4()),
                            "loc_id": loc_id,
                            "ts": dt,
                            "rain": p if p is not None else 0.0,
                            "temp": tp,
                            "hum": h
                        })
                        
                    if batch_params:
                        query = text("""
                            INSERT INTO weather_observations (id, location_id, timestamp, rainfall, temperature, humidity, source)
                            VALUES (:id, :loc_id, :ts, :rain, :temp, :hum, 'open-meteo')
                        """)
                        conn.execute(query, batch_params)
                        inserted = len(batch_params)
                        
                    print(f"Inserted {inserted} weather observations for {loc_id}")
                except Exception as e:
                    print(f"Error fetching weather for location {loc_id}: {e}")
                    
        print(f"[{datetime.utcnow()}] Successfully completed weather ingestion job.")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Weather ingestion job failed: {e}")

if __name__ == "__main__":
    if os.getenv("RUN_ONCE"):
        run_weather_job()
        run_job()
        sys.exit(0)

    import threading
    
    def weather_loop():
        run_weather_job()
        while True:
            time.sleep(weather_interval_minutes * 60)
            run_weather_job()
            
    def inference_loop():
        time.sleep(10) # wait for first weather sync
        run_job()
        while True:
            time.sleep(interval_minutes * 60)
            run_job()
            
    t1 = threading.Thread(target=weather_loop)
    t2 = threading.Thread(target=inference_loop)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
