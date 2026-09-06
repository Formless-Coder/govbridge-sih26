from fastapi.testclient import TestClient

from app.main import app


def test_case_audit_lists_events_for_a_single_case():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Audit Check'},
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

    response = client.get(f'/api/v1/cases/{case_id}/audit')
    assert response.status_code == 200
    body = response.json()
    assert body['case_id'] == case_id
    assert isinstance(body['records'], list)
    assert any(record['action'] == 'DEPARTMENT_CHECK_COMPLETED' for record in body['records'])
    assert any(record['action'] == 'CASE_CREATED' for record in body['records'])
