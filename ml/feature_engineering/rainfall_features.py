import pandas as pd
from ml.feature_engineering.config import FEATURE_WINDOWS


def compute_rainfall_features(weather_df, location_id, reference_time):
    features = {}
    df = weather_df[weather_df["location_id"] == location_id].copy()
    if df.empty:
        for w in FEATURE_WINDOWS:
            features[f"rainfall_{w}h"] = 0.0
        features["rainfall_intensity"] = 0.0
        features["rainfall_missing"] = True
        return features

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    ref = pd.to_datetime(reference_time)

    for w in FEATURE_WINDOWS:
        window_start = ref - pd.Timedelta(hours=w)
        subset = df[(df["timestamp"] > window_start) & (df["timestamp"] <= ref)]
        features[f"rainfall_{w}h"] = float(subset["rainfall"].sum()) if not subset.empty else 0.0

    recent = df[(df["timestamp"] > ref - pd.Timedelta(hours=6)) & (df["timestamp"] <= ref)]
    baseline = df[(df["timestamp"] > ref - pd.Timedelta(hours=168)) & (df["timestamp"] <= ref)]
    recent_rate = recent["rainfall"].mean() if not recent.empty else 0.0
    baseline_rate = baseline["rainfall"].mean() if not baseline.empty else 0.0
    features["rainfall_intensity"] = float(recent_rate - baseline_rate) if baseline_rate else float(recent_rate)
    features["rainfall_missing"] = False
    return features
