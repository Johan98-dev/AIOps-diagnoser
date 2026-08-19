from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.telemetry.otel import shutdown_telemetry

@pytest.fixture(scope="session", autouse=True)
def cleanup_telemetry():
    yield
    shutdown_telemetry()

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_dashboard():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "AIOps Diagnoser Console" in response.text

@patch("app.infrastructure.llm.client.LlmClient.generate_diagnosis", new_callable=AsyncMock)
def test_diagnose_mock(mock_generate_diagnosis):
    # Set the return value of the mocked LLM response
    mock_generate_diagnosis.return_value = {
        "summary": "Analysis of service 'payment-service' complete.",
        "root_cause": "Mocked root cause: High CPU usage due to unoptimized loops.",
        "impact_analysis": "Increased latency for downstream services.",
        "suggested_actions": [
            "Scale the service horizontally.",
            "Review the recent deployment for performance regressions.",
            "Enable profiling to identify the bottleneck."
        ],
        "confidence_score": 0.95
    }

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


@pytest.mark.anyio
async def test_telemetry_collector_offline_fallback():
    from app.infrastructure.telemetry.collector import TelemetryCollector
    collector = TelemetryCollector(base_url="http://invalid-localhost-9999")
    context = await collector.get_telemetry_context("test-service", lookback_minutes=5)
    assert context.service_name == "test-service"
    assert context.metadata["status"] == "offline_fallback"

