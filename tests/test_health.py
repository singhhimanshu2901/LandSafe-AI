"""
Phase 14: Basic API tests.
Run with: pytest tests/ (from backend/ dir, with backend deps installed)
"""
from fastapi.testclient import TestClient
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_locations_list_empty_or_valid():
    resp = client.get("/api/v1/locations")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_invalid_report_category_rejected():
    resp = client.post("/api/v1/reports", json={
        "lat": 26.1, "lon": 91.7, "category": "NOT_A_REAL_CATEGORY"
    })
    assert resp.status_code == 400
