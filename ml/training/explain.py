"""
Phase 7: Risk scoring + SHAP explainability.
"""
import joblib

try:
    import shap
except ImportError:
    shap = None


RISK_LEVELS = [
    (0, 20, "Very Low"),
    (21, 40, "Low"),
    (41, 60, "Moderate"),
    (61, 80, "High"),
    (81, 100, "Critical"),
]


def score_to_level(score):
    for lo, hi, label in RISK_LEVELS:
        if lo <= score <= hi:
            return label
    return "Unknown"


def load_model(model_path):
    return joblib.load(model_path)


def predict_with_explanation(model_bundle, X_row):
    model = model_bundle["model"]
    feature_cols = model_bundle["feature_cols"]
    X = X_row[feature_cols].fillna(-1).values.reshape(1, -1)

    prob = float(model.predict_proba(X)[0, 1])
    score = round(prob * 100, 2)
    level = score_to_level(score)

    top_factors = []
    if shap is not None:
        try:
            base_estimator = model.calibrated_classifiers_[0].estimator
            explainer = shap.TreeExplainer(base_estimator)
            shap_values = explainer.shap_values(X)
            contributions = list(zip(feature_cols, shap_values[0]))
            contributions.sort(key=lambda x: abs(x[1]), reverse=True)
            top_factors = [{"feature": f, "contribution": float(v)} for f, v in contributions[:5]]
        except Exception:
            top_factors = []

    return {
        "probability": prob,
        "score": score,
        "level": level,
        "top_factors": top_factors,
    }
