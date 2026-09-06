from fastapi.testclient import TestClient

from app.main import app


def test_notifications_are_created_for_case_updates():
    client = TestClient(app)

    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Aman Giri'},
    )
    case_id = created.json()['case_id']

    notify = client.post(
        '/api/v1/notifications',
        json={
            'case_id': case_id,
            'channel': 'email',
            'message': 'Your scholarship application is under review.',
            'recipient': 'aman@example.com',
        },
    )

    assert notify.status_code == 201
    body = notify.json()
    assert body['case_id'] == case_id
    assert body['channel'] == 'email'
    assert body['status'] == 'queued'

    list_response = client.get('/api/v1/notifications')
    assert list_response.status_code == 200
    assert any(item['case_id'] == case_id for item in list_response.json()['notifications'])
