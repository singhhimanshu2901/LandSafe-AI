import pandas as pd


def compute_moisture_features(sensor_df, location_id, reference_time):
    features = {}
    # sensor readings aren't directly tied to location_id in schema; caller should pre-filter by nearby sensor_id
    df = sensor_df.copy()
    if df.empty:
        return {
            "moisture_latest": None,
            "moisture_avg_24h": None,
            "moisture_delta": None,
            "moisture_missing": True,
        }

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    ref = pd.to_datetime(reference_time)
    df = df[df["timestamp"] <= ref].sort_values("timestamp")

    if df.empty:
        return {
            "moisture_latest": None,
            "moisture_avg_24h": None,
            "moisture_delta": None,
            "moisture_missing": True,
        }

    latest = df.iloc[-1]["soil_moisture"]
    window_24h = df[df["timestamp"] > ref - pd.Timedelta(hours=24)]
    avg_24h = window_24h["soil_moisture"].mean() if not window_24h.empty else None

    delta = None
    if len(df) >= 2:
        delta = float(df.iloc[-1]["soil_moisture"] - df.iloc[-2]["soil_moisture"])

    features["moisture_latest"] = float(latest) if latest is not None else None
    features["moisture_avg_24h"] = float(avg_24h) if avg_24h is not None else None
    features["moisture_delta"] = delta
    features["moisture_missing"] = False
    return features
