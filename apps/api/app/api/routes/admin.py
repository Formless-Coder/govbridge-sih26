from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.core.auth import require_roles

router = APIRouter(tags=['admin'])

ADMIN_CONFIG: dict[str, Any] = {
    'service_catalog': [
        {'service_id': 'scholarship', 'name': 'Scholarship support', 'enabled': True, 'department': 'Social welfare'},
        {'service_id': 'housing', 'name': 'Housing assistance', 'enabled': True, 'department': 'Urban services'},
        {'service_id': 'health', 'name': 'Health subsidy', 'enabled': False, 'department': 'Public health'},
    ],
    'slas': {
        'review_hours': 72,
        'decision_hours': 24,
        'appeal_hours': 120,
    },
    'notifications': {
        'email': True,
        'sms': False,
        'push': True,
    },
    'workflow': {
        'auto_assign': True,
        'escalation_enabled': True,
    },
}


def _deep_update(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_update(base[key], value)
        else:
            base[key] = value
    return base


@router.get('/admin/config')
def get_admin_config():
    return ADMIN_CONFIG


@router.get('/admin/configuration')
def get_admin_configuration():
    return ADMIN_CONFIG


@router.patch('/admin/config')
def update_admin_config(request: Request, body: dict[str, Any]):
    require_roles(request, ['admin'])
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail='Configuration payload must be an object')
    _deep_update(ADMIN_CONFIG, body)
    return ADMIN_CONFIG


@router.get('/admin/audit')
def get_admin_audit_dashboard(request: Request):
    require_roles(request, ['admin'])
    from app.api.routes.cases import AUDIT_LOGS, CASE_STORE

    total_cases = len(CASE_STORE)
    decision_made = sum(1 for case in CASE_STORE.values() if case.get('decision', {}).get('decision'))
    under_review = sum(1 for case in CASE_STORE.values() if case.get('status') in {'UNDER_REVIEW', 'IN_REVIEW'})
    audit_records = len(AUDIT_LOGS)

    recent_activity = []
    for entry in reversed(AUDIT_LOGS[-8:]):
        recent_activity.append({
            'case_id': entry.get('case_id'),
            'actor': entry.get('actor'),
            'action': entry.get('action'),
            'resource': entry.get('resource'),
            'purpose': entry.get('purpose'),
            'outcome': entry.get('outcome'),
            'timestamp': entry.get('timestamp', '2026-09-07T00:00:00Z'),
        })

    return {
        'summary': {
            'total_cases': total_cases,
            'decision_made': decision_made,
            'under_review': under_review,
            'audit_records': audit_records,
        },
        'recent_activity': recent_activity,
    }
