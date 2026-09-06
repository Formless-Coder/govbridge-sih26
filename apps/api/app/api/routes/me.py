from fastapi import APIRouter, Depends, Request, status

from app.core.auth import get_bearer_token, get_roles_from_token, get_subject_from_token, validate_token

router = APIRouter(tags=['identity'])


@router.get('/me')
def get_me(request: Request):
    token = get_bearer_token(request)
    payload = validate_token(token)
    subject_id = get_subject_from_token(payload)
    roles = get_roles_from_token(payload)
    return {
        'subject_id': subject_id,
        'roles': roles,
        'provider': 'keycloak',
        'issuer': payload.get('iss'),
    }


@router.get('/me/roles')
def get_my_roles(request: Request):
    token = get_bearer_token(request)
    payload = validate_token(token)
    subject_id = get_subject_from_token(payload)
    roles = get_roles_from_token(payload)
    return {
        'subject_id': subject_id,
        'roles': roles,
    }
