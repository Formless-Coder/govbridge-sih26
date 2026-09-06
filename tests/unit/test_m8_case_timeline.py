from fastapi.testclient import TestClient

from app.main import app


def test_case_timeline_lists_status_changes_and_events():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Timeline Check'},
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

    response = client.get(f'/api/v1/cases/{case_id}/timeline')
    assert response.status_code == 200
    body = response.json()
    assert body['case_id'] == case_id
    assert body['status'] == 'DECISION_MADE'
    assert any(item['event'] == 'DEPARTMENT_CHECK' for item in body['events'])
    assert any(item['event'] == 'DECISION_MADE' for item in body['events'])
