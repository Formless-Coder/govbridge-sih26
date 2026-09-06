from fastapi.testclient import TestClient

from app.main import app


def test_case_detail_contract_returns_status_timeline_and_decision():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Citizen Portal User'},
    )
    assert created.status_code == 201
    case_id = created.json()['case_id']

    client.post(
        f'/api/v1/cases/{case_id}/consents',
        json={'purpose': 'scholarship_eligibility', 'attributes': ['income.status'], 'decision': 'approve'},
    )
    client.post(
        f'/api/v1/cases/{case_id}/department-checks',
        json={'department_id': 'income', 'service_id': 'scholarship', 'payload': {'status': 'employed', 'monthly_income': 45000}},
    )
    client.post(
        f'/api/v1/cases/{case_id}/decisions',
        json={'decision': 'approved', 'reason': 'Income and enrollment verified'},
    )

    response = client.get(f'/api/v1/cases/{case_id}')
    assert response.status_code == 200
    payload = response.json()
    assert payload['case_id'] == case_id
    assert payload['service_id'] == 'scholarship'
    assert payload['status'] in {'UNDER_REVIEW', 'DECISION_MADE', 'COMPLETED'}
    assert payload['decision']['decision'] == 'approved'
    assert payload['timeline']
