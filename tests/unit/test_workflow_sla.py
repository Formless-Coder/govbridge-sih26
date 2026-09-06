from fastapi.testclient import TestClient

from app.main import app


def test_workflow_and_sla_tracking_is_available():
    client = TestClient(app)

    created = client.post(
        '/api/v1/workflows',
        json={
            'case_id': 'CASE-100',
            'service_id': 'scholarship',
            'sla_hours': 48,
        },
    )

    assert created.status_code == 201
    body = created.json()
    assert body['case_id'] == 'CASE-100'
    assert body['status'] == 'in_progress'
    assert body['sla_hours'] == 48

    fetched = client.get('/api/v1/workflows/CASE-100')
    assert fetched.status_code == 200
    fetched_body = fetched.json()
    assert fetched_body['current_stage'] == 'submission'
    assert fetched_body['sla']['hours_remaining'] > 0

    stage_update = client.post(
        '/api/v1/workflows/CASE-100/stages',
        json={'stage': 'review', 'status': 'in_progress'},
    )
    assert stage_update.status_code == 200
    assert stage_update.json()['current_stage'] == 'review'

    all_workflows = client.get('/api/v1/workflows')
    assert all_workflows.status_code == 200
    assert any(item['case_id'] == 'CASE-100' for item in all_workflows.json()['workflows'])
