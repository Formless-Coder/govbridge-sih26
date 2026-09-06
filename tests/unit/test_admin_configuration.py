from fastapi.testclient import TestClient

from app.main import app


def test_admin_configuration_returns_and_updates_settings():
    client = TestClient(app)

    response = client.get('/api/v1/admin/config')
    assert response.status_code == 200
    payload = response.json()
    assert 'service_catalog' in payload
    assert 'slas' in payload
    assert 'notifications' in payload

    update = client.patch(
        '/api/v1/admin/config',
        json={
            'notifications': {'email': True, 'sms': True, 'push': False},
            'slas': {'review_hours': 48},
        },
    )
    assert update.status_code == 200
    updated = update.json()
    assert updated['notifications']['sms'] is True
    assert updated['slas']['review_hours'] == 48

    fetched = client.get('/api/v1/admin/configuration')
    assert fetched.status_code == 200
    assert fetched.json()['slas']['review_hours'] == 48
