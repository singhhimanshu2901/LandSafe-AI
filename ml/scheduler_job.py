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

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "backend"))

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
                except Exception as e:
                    print(f"Error predicting for location {row.get('location_id')}: {e}")
                    
        # Now trigger the early warning engine with a proper Session
        if Session:
            with Session() as db_session:
                from app.services.early_warning import evaluate_and_generate_alert
                from app.models.risk_prediction import RiskPrediction
                
                # We need to evaluate the newly inserted predictions
                # Just fetch the latest prediction for each location generated in the last few minutes
                recent_preds = db_session.query(RiskPrediction).filter(
                    RiskPrediction.timestamp >= (datetime.utcnow() - timedelta(minutes=5))
                ).all()
                
                for rp in recent_preds:
                    evaluate_and_generate_alert(db_session, rp, str(rp.location_id))
                    
        print(f"[{datetime.utcnow()}] Successfully completed inference job.")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Inference job failed: {e}")
        if os.getenv("RUN_ONCE"):
            raise

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
                        if os.getenv("RUN_ONCE"):
                            raise
                        continue
                    print(f"Received weather for {loc_id}, status={res.status_code}")
                    if res.status_code != 200:
                        print(f"Failed to fetch weather for {loc_id}: {res.status_code} {res.text}")
                        if os.getenv("RUN_ONCE"):
                            raise RuntimeError(f"Failed to fetch weather for {loc_id}")
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
                    if os.getenv("RUN_ONCE"):
                        raise
                    
        print(f"[{datetime.utcnow()}] Successfully completed weather ingestion job.")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Weather ingestion job failed: {e}")
        if os.getenv("RUN_ONCE"):
            raise

if __name__ == "__main__":
    if os.getenv("RUN_ONCE"):
        try:
            run_weather_job()
            run_job()
            sys.exit(0)
        except Exception as e:
            print(f"Fatal error during RUN_ONCE execution: {e}")
            sys.exit(1)

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
