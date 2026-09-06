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


def test_me_requires_bearer_token():
    client = TestClient(app)
    response = client.get('/api/v1/me')

    assert response.status_code == 401


def test_me_returns_subject_and_roles_for_valid_token():
    client = TestClient(app)
    token = make_token(sub='citizen-user-001', roles=['citizen'])
    response = client.get('/api/v1/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    payload = response.json()
    assert payload['subject_id']
    assert payload['roles'] == ['citizen']
    assert payload['provider'] == 'keycloak'


def test_me_roles_uses_internal_subject_mapping():
    client = TestClient(app)
    token = make_token(sub='officer-user-007', roles=['officer', 'admin'])
    response = client.get('/api/v1/me/roles', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    payload = response.json()
    assert payload['subject_id']
    assert 'officer' in payload['roles']
    assert 'admin' in payload['roles']


def test_invalid_token_is_rejected():
    client = TestClient(app)
    response = client.get('/api/v1/me', headers={'Authorization': 'Bearer invalid-token'})

    assert response.status_code == 401
