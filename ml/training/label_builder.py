"""
Phase 5: Historical landslide dataset prep + labeling.

Builds a supervised training set by joining feature rows (from the feature
engineering pipeline) with landslide event outcomes. A location+time row is
labeled positive (1) if a verified landslide event occurred within a spatial
radius and a short time window after the reference_time; otherwise negative (0).
"""
import pandas as pd
from shapely.geometry import Point

POSITIVE_RADIUS_KM = 3.0
POSITIVE_WINDOW_HOURS = 72


def label_feature_table(feature_df, landslide_events_gdf, location_lookup):
    """
    feature_df: output of build_feature_table (one row per location/reference_time)
    landslide_events_gdf: GeoDataFrame of verified landslide_events
    location_lookup: dict {location_id: (lat, lon)}
    """
    labels = []
    events = landslide_events_gdf[landslide_events_gdf.get("verification_status") == "verified"] \
        if "verification_status" in landslide_events_gdf.columns else landslide_events_gdf

    for _, row in feature_df.iterrows():
        loc_id = row["location_id"]
        if loc_id not in location_lookup:
            labels.append(0)
            continue
        lat, lon = location_lookup[loc_id]
        point = Point(lon, lat)

        ref_time = pd.to_datetime(row["reference_time"])
        window_end = ref_time + pd.Timedelta(hours=POSITIVE_WINDOW_HOURS)

        is_positive = 0
        if events is not None and len(events) > 0:
            nearby = events.copy()
            nearby["event_time"] = pd.to_datetime(nearby["event_time"])
            nearby = nearby[(nearby["event_time"] >= ref_time) & (nearby["event_time"] <= window_end)]
            if len(nearby) > 0:
                dist_km = nearby.geometry.distance(point) * 111.0
                if (dist_km <= POSITIVE_RADIUS_KM).any():
                    is_positive = 1

        labels.append(is_positive)

    feature_df = feature_df.copy()
    feature_df["label"] = labels
    return feature_df
