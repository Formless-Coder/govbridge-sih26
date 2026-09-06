from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_is_reachable():
    client = TestClient(app)
    response = client.get('/api/v1/health')

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'


def test_ready_endpoint_reports_dependencies():
    client = TestClient(app)
    response = client.get('/api/v1/ready')

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] in {'ok', 'degraded'}
    assert 'dependencies' in payload
