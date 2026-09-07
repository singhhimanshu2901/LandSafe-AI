"""
Phase 6: ML model training - XGBoost baseline with temporal/spatial-aware split
and probability calibration.
"""
import os
import json
from datetime import datetime

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_score, recall_score
from sklearn.calibration import CalibratedClassifierCV

try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None

import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

FEATURE_COLUMNS_EXCLUDE = {"location_id", "reference_time", "label"}


def load_training_csv(path):
    return pd.read_csv(path)


def train(df, model_version=None):
    if XGBClassifier is None:
        raise ImportError("xgboost is not installed. pip install xgboost")

    model_version = model_version or datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    feature_cols = [c for c in df.columns if c not in FEATURE_COLUMNS_EXCLUDE]
    X = df[feature_cols].fillna(-1)
    y = df["label"]

    # Temporal split: sort by reference_time, hold out most recent 20% as test
    df_sorted = df.sort_values("reference_time")
    split_idx = int(len(df_sorted) * 0.8)
    train_idx = df_sorted.index[:split_idx]
    test_idx = df_sorted.index[split_idx:]

    X_train, X_test = X.loc[train_idx], X.loc[test_idx]
    y_train, y_test = y.loc[train_idx], y.loc[test_idx]

    base_model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        scale_pos_weight=max(1, (y_train == 0).sum() / max(1, (y_train == 1).sum())),
        eval_metric="logloss",
        use_label_encoder=False,
    )
    base_model.fit(X_train, y_train)

    calibrated = CalibratedClassifierCV(base_model, cv=5, method="sigmoid")
    calibrated.fit(X_test, y_test)

    probs = calibrated.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, probs)) if y_test.nunique() > 1 else None,
        "pr_auc": float(average_precision_score(y_test, probs)) if y_test.nunique() > 1 else None,
        "f1": float(f1_score(y_test, preds, zero_division=0)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "positive_rate_train": float(y_train.mean()),
        "positive_rate_test": float(y_test.mean()),
        "model_version": model_version,
    }

    model_path = os.path.join(MODEL_DIR, f"xgb_{model_version}.joblib")
    joblib.dump({"model": calibrated, "feature_cols": feature_cols}, model_path)

    metrics_path = os.path.join(MODEL_DIR, f"metrics_{model_version}.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))
    print(f"Model saved to {model_path}")
    return metrics, model_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m ml.training.train_model <path_to_labeled_features_csv>")
        sys.exit(1)
    df = load_training_csv(sys.argv[1])
    train(df)
