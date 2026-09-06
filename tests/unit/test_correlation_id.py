from fastapi.testclient import TestClient

from app.main import app


def test_correlation_id_is_generated_for_requests():
    client = TestClient(app)
    response = client.get('/api/v1/health')

    assert response.status_code == 200
    assert 'X-Correlation-ID' in response.headers
    assert response.headers['X-Correlation-ID']


def test_correlation_id_is_propagated_when_present():
    client = TestClient(app)
    response = client.get('/api/v1/health', headers={'X-Correlation-ID': 'trace-123'})

    assert response.status_code == 200
    assert response.headers['X-Correlation-ID'] == 'trace-123'
