import os
import joblib
import pandas as pd
from datetime import datetime

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

class RiskInferencePipeline:
    def __init__(self, model_version=None):
        if model_version:
            self.model_path = os.path.join(MODEL_DIR, f"xgb_{model_version}.joblib")
            self.model_version = model_version
        else:
            # find latest model
            if not os.path.exists(MODEL_DIR):
                raise FileNotFoundError(f"Model directory not found: {MODEL_DIR}")
            models = [f for f in os.listdir(MODEL_DIR) if f.startswith("xgb_") and f.endswith(".joblib")]
            if not models:
                raise FileNotFoundError("No trained model found in ml/models/")
            latest_model = sorted(models)[-1]
            self.model_path = os.path.join(MODEL_DIR, latest_model)
            self.model_version = latest_model.replace("xgb_", "").replace(".joblib", "")
        
        artifact = joblib.load(self.model_path)
        self.model = artifact["model"]
        self.feature_cols = artifact["feature_cols"]

    def predict(self, feature_record):
        # feature_record is a dict of features for one location
        df = pd.DataFrame([feature_record])
        
        # validate features
        missing_cols = [c for c in self.feature_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing features required for inference: {missing_cols}")
            
        for c in self.feature_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')
            
        X = df[self.feature_cols].fillna(-1)
        
        # Check for missing critical data
        if df.get('rainfall_missing', [False])[0]:
            return {
                "probability": None,
                "level": "DATA UNAVAILABLE",
                "model_version": self.model_version,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "DATA UNAVAILABLE",
                "details": {"human_explanation": "Critical rainfall data is missing.", "top_features": []}
            }
            
        probs = self.model.predict_proba(X)
        prob = float(probs[0, 1])
        
        level = "LOW"
        if prob > 0.8:
            level = "CRITICAL"
        elif prob > 0.6:
            level = "HIGH"
        elif prob > 0.3:
            level = "MEDIUM"
            
        # Explainable AI layer (pseudo-SHAP)
        # Using feature_importances_ and actual input magnitudes.
        importances = self.model.feature_importances_
        feature_contributions = []
        for i, col in enumerate(self.feature_cols):
            val = float(X.iloc[0, i])
            # pseudo-contribution logic: high feature value + high importance
            # we know for this model, higher rainfall = higher risk
            contrib = val * importances[i]
            if val > 0:
                feature_contributions.append({"feature": col, "value": val, "importance": importances[i], "contrib": contrib})
                
        feature_contributions.sort(key=lambda x: x["contrib"], reverse=True)
        top_features = feature_contributions[:3]
        
        if level == "LOW":
            human_explanation = "Current conditions indicate relatively low risk due to lack of extreme rainfall or destabilizing environmental factors."
        else:
            factors = [f.get("feature").replace("_", " ") for f in top_features]
            human_explanation = f"Risk elevated to {level}. Main contributing factors: {', '.join(factors)}."
            
        return {
            "probability": prob,
            "level": level,
            "model_version": self.model_version,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "DATA AVAILABLE",
            "details": {
                "top_features": top_features,
                "human_explanation": human_explanation
            }
        }

if __name__ == "__main__":
    # Test script
    import sys
    try:
        pipeline = RiskInferencePipeline()
        print(f"Loaded model version: {pipeline.model_version}")
        print(f"Features: {pipeline.feature_cols}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
