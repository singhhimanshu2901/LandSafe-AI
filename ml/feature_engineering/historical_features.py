import numpy as np

def compute_historical_features(landslide_events_gdf, location_row, radius_km=5):
    features = {"history_event_count": 0, "history_nearest_distance_km": None}

    if landslide_events_gdf is None or len(landslide_events_gdf) == 0:
        return features

    lat, lon = location_row["lat"], location_row["lon"]
    
    # approximate degrees->km conversion
    # 1 degree lat approx 111km, 1 degree lon approx 111km * cos(lat)
    dlat = (landslide_events_gdf["lat"] - lat) * 111.0
    dlon = (landslide_events_gdf["lon"] - lon) * 111.0 * np.cos(np.radians(lat))
    
    distances_km = np.sqrt(dlat**2 + dlon**2)

    features["history_event_count"] = int((distances_km <= radius_km).sum())
    features["history_nearest_distance_km"] = float(distances_km.min()) if len(distances_km) > 0 else None
    return features
