from fastapi.testclient import TestClient

from app.main import app


def test_case_decision_is_recorded_and_exposed():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Aman Giri'},
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

    response = client.post(
        f'/api/v1/cases/{case_id}/decisions',
        json={'decision': 'approved', 'reason': 'Income verified and policy thresholds passed.'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['decision'] == 'approved'
    assert body['case_id'] == case_id

    case_response = client.get(f'/api/v1/cases/{case_id}')
    assert case_response.status_code == 200
    assert case_response.json()['decision']['decision'] == 'approved'


def test_decision_queue_lists_recent_outcomes():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Case Queue'},
    )
    case_id = created.json()['case_id']

    client.post(
        f'/api/v1/cases/{case_id}/decisions',
        json={'decision': 'referred', 'reason': 'Manual review required.'},
    )

    response = client.get('/api/v1/decisions')
    assert response.status_code == 200
    payload = response.json()
    assert any(item['case_id'] == case_id for item in payload['decisions'])
