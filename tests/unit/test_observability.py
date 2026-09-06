from fastapi.testclient import TestClient

from app.main import app


def test_observability_metrics_and_health_summary_are_available():
    client = TestClient(app)

    response = client.get('/api/v1/observability')
    assert response.status_code == 200

    payload = response.json()
    assert 'metrics' in payload
    assert 'logs' in payload
    assert 'traces' in payload
    assert payload['metrics']['total_requests'] >= 0
    assert isinstance(payload['logs'], list)
    assert isinstance(payload['traces'], list)
