from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=['decisions'])

DECISION_STORE: list[dict[str, Any]] = []


@router.post('/cases/{case_id}/decisions')
def record_decision(case_id: str, body: dict[str, Any]):
    decision = (body.get('decision') or '').strip().lower()
    if not decision:
        raise HTTPException(status_code=400, detail='Decision required')

    entry = {
        'case_id': case_id,
        'decision': decision,
        'reason': body.get('reason', ''),
        'recorded_at': '2026-09-07T00:00:00Z',
    }
    if entry not in DECISION_STORE:
        DECISION_STORE.append(entry)
    return entry


@router.get('/decisions')
def list_decisions():
    return {'decisions': DECISION_STORE}
