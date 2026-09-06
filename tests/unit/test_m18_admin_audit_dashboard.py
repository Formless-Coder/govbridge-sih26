from fastapi.testclient import TestClient

from app.main import app


def test_admin_audit_dashboard_returns_summary_and_recent_activity():
    client = TestClient(app)

    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Audit Admin User'},
    )
    assert created.status_code == 201
    case_id = created.json()['case_id']

    client.post(
        f'/api/v1/cases/{case_id}/department-checks',
        json={'department_id': 'income', 'service_id': 'scholarship', 'payload': {'status': 'employed', 'monthly_income': 45000}},
    )
    client.post(
        f'/api/v1/cases/{case_id}/decisions',
        json={'decision': 'approved', 'reason': 'Verified and eligible'},
    )

    response = client.get('/api/v1/admin/audit')
    assert response.status_code == 200
    payload = response.json()

    assert payload['summary']['total_cases'] >= 1
    assert payload['summary']['decision_made'] >= 1
    assert payload['summary']['audit_records'] >= 3
    assert any(item['case_id'] == case_id for item in payload['recent_activity'])
