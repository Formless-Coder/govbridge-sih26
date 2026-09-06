from fastapi.testclient import TestClient

from app.main import app


def test_citizen_dashboard_returns_services_cases_and_notifications():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Citizen Portal User'},
    )
    assert created.status_code == 201
    case_id = created.json()['case_id']

    consent = client.post(
        f'/api/v1/cases/{case_id}/consents',
        json={
            'purpose': 'scholarship_eligibility',
            'attributes': ['income.status'],
            'decision': 'approve',
        },
    )
    assert consent.status_code == 201

    check = client.post(
        f'/api/v1/cases/{case_id}/department-checks',
        json={
            'department_id': 'income',
            'service_id': 'scholarship',
            'payload': {'status': 'employed', 'monthly_income': 45000},
        },
    )
    assert check.status_code == 200

    response = client.get('/api/v1/citizen/dashboard')

    assert response.status_code == 200
    payload = response.json()
    assert any(service['id'] == 'scholarship' for service in payload['services'])
    assert any(case['case_id'] == case_id for case in payload['cases'])
    assert payload['stats']['active_cases'] >= 1
    assert payload['notifications']
