from fastapi.testclient import TestClient

from app.main import app


def test_case_notifications_are_generated_for_status_changes():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Notification Check'},
    )
    case_id = created.json()['case_id']

    client.post(
        f'/api/v1/cases/{case_id}/department-checks',
        json={
            'department_id': 'income',
            'service_id': 'scholarship',
            'payload': {'status': 'employed', 'monthly_income': 45000},
        },
    )
    client.post(
        f'/api/v1/cases/{case_id}/decisions',
        json={'decision': 'approved', 'reason': 'Income verified.'},
    )

    response = client.get(f'/api/v1/cases/{case_id}/notifications')
    assert response.status_code == 200
    body = response.json()
    assert body['case_id'] == case_id
    assert isinstance(body['notifications'], list)
    assert any('DECISION_MADE' in item.get('message', '') or item.get('event') == 'DECISION_MADE' for item in body['notifications'])


def test_global_notifications_feed_lists_recent_updates():
    client = TestClient(app)
    response = client.get('/api/v1/notifications')
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload['notifications'], list)
