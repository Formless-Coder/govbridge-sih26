import jwt

from fastapi.testclient import TestClient

from app.main import app

SECRET = 'govbridge-dev-secret'


def make_token(*, sub: str, roles: list[str], issuer: str = 'https://keycloak.example.com/realms/govbridge', audience: str = 'govbridge-api'):
    payload = {
        'iss': issuer,
        'sub': sub,
        'aud': audience,
        'roles': roles,
        'exp': 4102444800,
    }
    return jwt.encode(payload, SECRET, algorithm='HS256')


def test_review_queue_requires_officer_or_admin_role():
    client = TestClient(app)
    token = make_token(sub='citizen-user-021', roles=['citizen'])

    response = client.get('/api/v1/review-queue', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 403
    assert response.json()['detail'] == 'Insufficient permissions'


def test_admin_audit_requires_admin_role():
    client = TestClient(app)
    token = make_token(sub='officer-user-002', roles=['officer'])

    response = client.get('/api/v1/admin/audit', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 403
    assert response.json()['detail'] == 'Insufficient permissions'


def test_officer_role_can_access_review_queue():
    client = TestClient(app)
    token = make_token(sub='officer-user-007', roles=['officer'])

    response = client.get('/api/v1/review-queue', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    payload = response.json()
    assert 'cases' in payload
