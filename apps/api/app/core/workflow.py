from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


WORKFLOW_STORE: dict[str, dict[str, Any]] = {}


def _timestamp() -> str:
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


def _hours_remaining(started_at: str, sla_hours: int) -> float:
    started = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
    elapsed = (datetime.now(UTC) - started).total_seconds() / 3600
    return max(0.0, float(sla_hours) - elapsed)


def create_workflow(*, case_id: str, service_id: str, sla_hours: int = 48) -> dict[str, Any]:
    workflow = {
        'case_id': case_id,
        'service_id': service_id,
        'status': 'in_progress',
        'sla_hours': sla_hours,
        'current_stage': 'submission',
        'stages': [
            {'name': 'submission', 'status': 'completed'},
            {'name': 'review', 'status': 'pending'},
            {'name': 'decision', 'status': 'pending'},
        ],
        'started_at': _timestamp(),
        'updated_at': _timestamp(),
        'sla': {
            'target_hours': sla_hours,
            'hours_remaining': float(sla_hours),
            'breached': False,
        },
    }
    WORKFLOW_STORE[case_id] = workflow
    return workflow


def get_workflow(case_id: str) -> dict[str, Any] | None:
    workflow = WORKFLOW_STORE.get(case_id)
    if not workflow:
        return None
    remaining = _hours_remaining(workflow['started_at'], workflow['sla_hours'])
    workflow['sla'] = {
        'target_hours': workflow['sla_hours'],
        'hours_remaining': round(remaining, 2),
        'breached': remaining <= 0,
    }
    workflow['updated_at'] = _timestamp()
    return workflow


def list_workflows() -> list[dict[str, Any]]:
    return [get_workflow(case_id) for case_id in WORKFLOW_STORE]


def update_stage(case_id: str, *, stage: str, status: str) -> dict[str, Any]:
    workflow = WORKFLOW_STORE.get(case_id)
    if not workflow:
        raise KeyError(f'Workflow not found: {case_id}')

    for item in workflow['stages']:
        if item['name'] == stage:
            item['status'] = status
    workflow['current_stage'] = stage
    workflow['status'] = 'in_progress' if status != 'completed' else 'completed'
    workflow['updated_at'] = _timestamp()
    return get_workflow(case_id)
