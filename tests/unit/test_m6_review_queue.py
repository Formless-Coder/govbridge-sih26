from fastapi.testclient import TestClient

from app.main import app


def test_review_queue_returns_cases_ready_for_manual_review():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Review Queue'},
    )
    case_id = created.json()['case_id']

    client.post(
        f'/api/v1/cases/{case_id}/decisions',
        json={'decision': 'referred', 'reason': 'Manual review required.'},
    )

    response = client.get('/api/v1/review-queue')
    assert response.status_code == 200
    payload = response.json()
    assert any(item['case_id'] == case_id for item in payload['cases'])


def test_officer_can_take_a_case_for_manual_review():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Officer Action'},
    )
    case_id = created.json()['case_id']

    response = client.post(
        f'/api/v1/cases/{case_id}/review',
        json={'assignee': 'officer-42', 'notes': 'Needs additional income verification.'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['case_id'] == case_id
    assert body['assignee'] == 'officer-42'

    case_response = client.get(f'/api/v1/cases/{case_id}')
    assert case_response.status_code == 200
    assert case_response.json()['review']['assignee'] == 'officer-42'
