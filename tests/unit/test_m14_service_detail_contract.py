from fastapi.testclient import TestClient

from app.main import app


def test_service_detail_contract_exposes_applicant_details():
    client = TestClient(app)
    response = client.get('/api/v1/services/scholarship')

    assert response.status_code == 200
    payload = response.json()
    assert payload['id'] == 'scholarship'
    assert payload['name'] == 'Scholarship Eligibility'
    assert payload['description']
    assert payload['required_documents']
    assert payload['eligibility_summary']
    assert payload['estimated_time_days'] > 0
