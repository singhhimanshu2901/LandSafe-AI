# Landsafe AI

AI-Powered Early Warning & Landslide Risk Monitoring System for the North Eastern Region (NER).
Built for Smart India Hackathon 2026 — Problem Statement SIH26001.

## Project Structure
- `backend/` — FastAPI backend (auth, ingestion, risk, GIS, reports, alerts APIs) + PostgreSQL/PostGIS via Alembic
- `ml/` — Feature engineering pipeline, model training (XGBoost), SHAP explainability
- `frontend/` — React + Vite GIS dashboard + PWA field reporting app
- `tests/` — pytest test suite
- `docs/` — project documentation
- `infra/` — deployment configs (see docker-compose.yml at root)

## Quick Start (Docker - recommended)
```bash
docker-compose up --build
```
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Manual Setup

### 1. Database (PostgreSQL + PostGIS)
Install PostgreSQL with PostGIS extension, or run:
```bash
docker run -d --name landsafe-db -e POSTGRES_USER=landsafe -e POSTGRES_PASSWORD=landsafe -e POSTGRES_DB=landsafe -p 5432:5432 postgis/postgis:15-3.4
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit DATABASE_URL if needed
alembic upgrade head            # creates tables + PostGIS extension
uvicorn app.main:app --reload
```
Visit: http://127.0.0.1:8000/docs

### 3. ML Feature Pipeline
```bash
cd ..   # project root
pip install -r ml/requirements.txt
python -m ml.feature_engineering.pipeline
```
Output CSV: `ml/feature_engineering/output/features_<timestamp>.csv`

### 4. Model Training (after labeling features)
```bash
python -m ml.training.train_model <path_to_labeled_csv>
```
Requires `pip install xgboost shap joblib` (add to ml/requirements.txt if missing).

### 5. Frontend
```bash
cd frontend
npm install
npm run dev
```
Visit: http://localhost:5173

### 6. Run Tests
```bash
pip install pytest
pytest tests/ -v
```

## Core Value Proposition
Predict → Explain → Map → Prioritize → Warn → Collect Feedback

## Notes
- This is a hackathon-ready MVP scaffold. Real-time satellite/sensor integrations
  are stubbed and clearly marked with TODOs where DEM/SAR data would be integrated.
- Any simulated data used during demo must be explicitly labeled as simulated.
