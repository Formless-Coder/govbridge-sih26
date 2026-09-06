from fastapi.testclient import TestClient

from app.main import app


def test_officer_review_queue_returns_actionable_cases():
    client = TestClient(app)

    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Officer Queue User'},
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

    response = client.get('/api/v1/review-queue')
    assert response.status_code == 200
    payload = response.json()
    assert 'cases' in payload
    assert any(item['case_id'] == case_id for item in payload['cases'])
    assert payload['cases'][0]['status']
    assert payload['cases'][0]['applicant_name']
