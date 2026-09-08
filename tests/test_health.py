"""
Phase 14: Basic API tests.
Run with: pytest tests/ (from backend/ dir, with backend deps installed)
"""
from fastapi.testclient import TestClient
import sys, os

# Mock required production variables before importing FastAPI
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
os.environ["SECRET_KEY"] = "test-secret"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.main import app
from app.db.session import get_db

# Override the database dependency so it doesn't try to connect
def override_get_db():
    yield None

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json().get("status") in ["ok", "degraded"]
    assert "database" in resp.json()

def test_invalid_report_category_rejected():
    # Attempting to post a report without auth should give 401
    resp = client.post("/api/v1/reports", json={
        "lat": 26.1, "lon": 91.7, "category": "NOT_A_REAL_CATEGORY"
    })
    assert resp.status_code == 401
