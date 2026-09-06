from fastapi.testclient import TestClient

from app.main import app


def test_case_completion_marks_case_as_done_and_returns_summary():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Completion Check'},
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

    response = client.post(
        f'/api/v1/cases/{case_id}/complete',
        json={'outcome': 'approved', 'notes': 'Case closed.'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['case_id'] == case_id
    assert body['status'] == 'COMPLETED'
    assert body['outcome'] == 'approved'

    summary = client.get(f'/api/v1/cases/{case_id}/summary')
    assert summary.status_code == 200
    assert summary.json()['status'] == 'COMPLETED'
