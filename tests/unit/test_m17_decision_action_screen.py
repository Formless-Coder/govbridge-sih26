from fastapi.testclient import TestClient

from app.main import app


def test_decision_action_screen_records_approval_and_reason():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Decision User'},
    )
    assert created.status_code == 201
    case_id = created.json()['case_id']

    response = client.post(
        f'/api/v1/cases/{case_id}/decisions',
        json={'decision': 'approved', 'reason': 'Eligibility verified and all checks passed'},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['case_id'] == case_id
    assert payload['decision'] == 'approved'
    assert payload['reason']

    decisions = client.get('/api/v1/decisions')
    assert decisions.status_code == 200
    assert any(item['case_id'] == case_id for item in decisions.json()['decisions'])
