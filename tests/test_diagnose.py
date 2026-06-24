from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_diagnose_mock():
    payload = {
        "service_name": "payment-service",
        "lookback_minutes": 10,
        "error_message": "Connection timeout"
    }
    response = client.post("/api/v1/diagnose", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "report_id" in data
    assert data["context"]["service_name"] == "payment-service"
    assert data["diagnosis"]["confidence_score"] == 0.95
    assert "Mocked root cause" in data["diagnosis"]["root_cause"]
