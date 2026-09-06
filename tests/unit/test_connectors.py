from fastapi.testclient import TestClient

from app.main import app


def test_connector_registry_supports_http_and_message_protocols():
    client = TestClient(app)

    http_response = client.get('/api/v1/connectors')
    assert http_response.status_code == 200
    connectors = http_response.json()['connectors']
    assert any(item['name'] == 'income-http' for item in connectors)
    assert any(item['protocol'] == 'http' for item in connectors)

    message_response = client.get('/api/v1/connectors?protocol=message')
    assert message_response.status_code == 200
    message_connectors = message_response.json()['connectors']
    assert any(item['name'] == 'scholarship-events' for item in message_connectors)
