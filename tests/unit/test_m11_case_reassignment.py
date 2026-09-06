from fastapi.testclient import TestClient

from app.main import app


def test_case_reassignment_updates_assignee_and_status():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Reassignment Check'},
    )
    case_id = created.json()['case_id']

    client.post(
        f'/api/v1/cases/{case_id}/review',
        json={'assignee': 'officer-1', 'notes': 'Needs review.'},
    )

    response = client.post(
        f'/api/v1/cases/{case_id}/reassign',
        json={'assignee': 'officer-2', 'reason': 'Escalated to senior reviewer.'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['case_id'] == case_id
    assert body['assignee'] == 'officer-2'
    assert body['status'] == 'IN_REVIEW'

    case_response = client.get(f'/api/v1/cases/{case_id}')
    assert case_response.status_code == 200
    assert case_response.json()['review']['assignee'] == 'officer-2'
