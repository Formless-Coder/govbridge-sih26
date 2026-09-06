import os
from typing import Any

import jwt
from fastapi import HTTPException, Request, status


JWT_SECRET = os.getenv('JWT_SECRET', 'govbridge-dev-secret')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_AUDIENCE = os.getenv('JWT_AUDIENCE', 'govbridge-api')
JWT_ISSUER = os.getenv('JWT_ISSUER', 'https://keycloak.example.com/realms/govbridge')


def get_bearer_token(request: Request) -> str:
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing bearer token')
    return auth_header.split(' ', 1)[1]


def validate_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], audience=JWT_AUDIENCE, issuer=JWT_ISSUER)
    except Exception as exc:  # pragma: no cover - delegated to JWT validation
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token') from exc
    return payload


def get_subject_from_token(payload: dict[str, Any]) -> str:
    return payload.get('sub') or payload.get('subject_id') or 'synthetic-subject'


def get_roles_from_token(payload: dict[str, Any]) -> list[str]:
    roles = payload.get('roles', [])
    if not roles:
        realm_access = payload.get('realm_access', {})
        if isinstance(realm_access, dict):
            roles = realm_access.get('roles', [])
    if not roles:
        resource_access = payload.get('resource_access', {})
        if isinstance(resource_access, dict):
            for client_roles in resource_access.values():
                if isinstance(client_roles, dict):
                    client_values = client_roles.get('roles', [])
                    if client_values:
                        roles = client_values
                        break
    if isinstance(roles, str):
        return [roles]
    return [str(role) for role in roles]


def require_roles(request: Request, allowed_roles: list[str]) -> dict[str, Any] | None:
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        return None

    token = get_bearer_token(request)
    payload = validate_token(token)
    roles = get_roles_from_token(payload)
    normalized_roles = {str(role).lower() for role in roles}
    normalized_allowed = {str(role).lower() for role in allowed_roles}
    if not normalized_roles.intersection(normalized_allowed):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
    return payload
