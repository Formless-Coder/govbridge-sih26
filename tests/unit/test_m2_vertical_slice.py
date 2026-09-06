import re

import jwt
from fastapi.testclient import TestClient

from app.main import app


SECRET = 'govbridge-dev-secret'


def auth_headers(*, role='citizen'):
    payload = {
        'iss': 'https://keycloak.example.com/realms/govbridge',
        'sub': 'citizen-user-001',
        'aud': 'govbridge-api',
        'roles': [role],
        'exp': 4102444800,
    }
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return {'Authorization': f'Bearer {token}'}


def test_services_are_available():
    client = TestClient(app)
    response = client.get('/api/v1/services')

    assert response.status_code == 200
    names = {item['id'] for item in response.json()}
    assert 'scholarship' in names


def test_case_id_format_and_status_flow():
    client = TestClient(app)
    response = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Aman Giri'},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    payload = response.json()
    assert re.match(r'^GOV-\d{4}-\d{6}$', payload['case_id'])
    assert payload['status'] == 'DRAFT'


def test_consent_and_income_fetch_execute_policy_and_canonicalization():
    client = TestClient(app)
    create_response = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Aman Giri'},
        headers=auth_headers(),
    )
    case_id = create_response.json()['case_id']

    consent_response = client.post(
        f'/api/v1/cases/{case_id}/consents',
        json={'purpose': 'scholarship_eligibility', 'attributes': ['income.status'], 'decision': 'approve'},
        headers=auth_headers(),
    )
    assert consent_response.status_code == 201

    data_request_response = client.post(
        f'/api/v1/cases/{case_id}/data-requests',
        json={'purpose': 'scholarship_eligibility', 'attributes': ['income.status']},
        headers=auth_headers(),
    )
    assert data_request_response.status_code == 200
    result = data_request_response.json()
    assert result['status'] == 'completed'
    assert result['canonical']['income']['status'] == 'employed'
    assert result['provenance']['source_system'] == 'income_rest_mock'


def test_audit_is_recorded_for_case_activity():
    client = TestClient(app)
    create_response = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Aman Giri'},
        headers=auth_headers(),
    )
    case_id = create_response.json()['case_id']

    audit_response = client.get(f'/api/v1/audit?case_id={case_id}', headers=auth_headers())
    assert audit_response.status_code == 200
    records = audit_response.json()['records']
    assert any(record['resource'] == case_id for record in records)
