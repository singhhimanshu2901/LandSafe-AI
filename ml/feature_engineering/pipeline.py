import os
from datetime import datetime

import pandas as pd


from ml.feature_engineering.data_loader import (
    load_weather,
    load_sensors,
    load_locations,
    load_landslide_events,
)
from ml.feature_engineering.rainfall_features import compute_rainfall_features
from ml.feature_engineering.terrain_features import compute_terrain_features
from ml.feature_engineering.moisture_features import compute_moisture_features
from ml.feature_engineering.historical_features import compute_historical_features





def build_feature_table(reference_time, location_ids=None):
    locations = load_locations(location_ids)
    weather = load_weather()
    sensors = load_sensors()
    events = load_landslide_events()

    rows = []
    for _, loc in locations.iterrows():
        lat, lon = loc["lat"], loc["lon"]
        loc_dict = {"lat": lat, "lon": lon, "elevation": loc.get("elevation"), "slope": loc.get("slope")}

        rainfall_feats = compute_rainfall_features(weather, loc["id"], reference_time)
        terrain_feats = compute_terrain_features(loc_dict)
        moisture_feats = compute_moisture_features(sensors, loc["id"], reference_time)
        history_feats = compute_historical_features(events, loc_dict, radius_km=5)

        row = {
            "location_id": loc["id"],
            "reference_time": reference_time,
            **rainfall_feats,
            **terrain_feats,
            **moisture_feats,
            **history_feats,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        feature_cols = [c for c in df.columns if c not in ("location_id", "reference_time")]
        df["data_quality_score"] = df[feature_cols].notna().mean(axis=1)
    return df


if __name__ == "__main__":
    ref_time = datetime.utcnow()
    table = build_feature_table(reference_time=ref_time)

    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"features_{ref_time.strftime('%Y%m%d_%H%M%S')}.csv")
    table.to_csv(out_path, index=False)
    print(f"Saved {len(table)} rows to {out_path}")
