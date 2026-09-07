"""
Phase 14: Feature engineering unit tests (no live DB required).
"""
import sys, os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.feature_engineering.rainfall_features import compute_rainfall_features
from ml.feature_engineering.terrain_features import compute_terrain_features


def test_rainfall_features_empty_df():
    empty_df = pd.DataFrame(columns=["location_id", "timestamp", "rainfall"])
    feats = compute_rainfall_features(empty_df, "loc-1", "2026-01-01T00:00:00")
    assert feats["rainfall_missing"] is True
    assert feats["rainfall_24h"] == 0.0


def test_terrain_features_basic():
    loc = {"elevation": 1200.0, "slope": 35.0}
    feats = compute_terrain_features(loc)
    assert feats["terrain_elevation"] == 1200.0
    assert feats["terrain_slope"] == 35.0
    assert feats["terrain_aspect"] is None
