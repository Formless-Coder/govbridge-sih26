from fastapi.testclient import TestClient

from app.main import app


def test_department_catalog_is_available():
    client = TestClient(app)
    response = client.get('/api/v1/departments')

    assert response.status_code == 200
    payload = response.json()
    ids = {item['id'] for item in payload['departments']}
    assert 'income' in ids
    assert 'housing' in ids


def test_case_department_check_records_a_verified_result():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Aman Giri'},
    )
    case_id = created.json()['case_id']

    response = client.post(
        f'/api/v1/cases/{case_id}/department-checks',
        json={
            'department_id': 'income',
            'service_id': 'scholarship',
            'payload': {'status': 'employed', 'monthly_income': 45000},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body['status'] in {'verified', 'eligible'}
    assert body['department_id'] == 'income'

    case_response = client.get(f'/api/v1/cases/{case_id}')
    assert case_response.status_code == 200
    assert any(item['department_id'] == 'income' for item in case_response.json()['department_checks'])
