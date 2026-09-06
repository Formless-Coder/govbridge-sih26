from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.core.auth import require_roles

router = APIRouter(tags=['review'])


@router.get('/review-queue')
def list_review_queue(request: Request):
    require_roles(request, ['officer', 'admin'])
    from app.api.routes.cases import CASE_STORE

    cases = []
    for case in CASE_STORE.values():
        status = case.get('status')
        decision = case.get('decision', {})
        queue_item = {
            'case_id': case['case_id'],
            'service_id': case.get('service_id'),
            'applicant_name': case.get('applicant_name'),
            'status': status or 'NEW',
            'decision': decision,
            'submitted_at': case.get('submitted_at', '2026-09-07T00:00:00Z'),
            'review_priority': 'High' if status in {'UNDER_REVIEW', 'IN_REVIEW'} else 'Normal',
        }
        if status in {'UNDER_REVIEW', 'IN_REVIEW', 'DECISION_MADE'} or decision.get('decision') == 'referred':
            cases.append(queue_item)
    return {'cases': cases}
