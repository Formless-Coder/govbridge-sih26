from fastapi.testclient import TestClient

from app.main import app


def test_case_summary_includes_status_and_latest_decision():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Summary Check'},
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

    response = client.get(f'/api/v1/cases/{case_id}/summary')
    assert response.status_code == 200
    body = response.json()
    assert body['case_id'] == case_id
    assert body['status'] == 'DECISION_MADE'
    assert body['decision']['decision'] == 'approved'
    assert body['latest_department_check']['department_id'] == 'income'


def test_case_listing_returns_summary_rows():
    client = TestClient(app)
    response = client.get('/api/v1/cases')
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert all('case_id' in item for item in payload)
