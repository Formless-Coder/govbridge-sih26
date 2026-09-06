from __future__ import annotations

import base64
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request, UploadFile, status

from app.core.case_id import generate_case_id
from app.core.connector import canonicalize_income, fetch_income_data
from app.core.database import list_case_records, save_case_record
from app.core.policy import evaluate_policy

router = APIRouter(tags=['cases'])

CASE_STORE: dict[str, dict[str, Any]] = {record['case_id']: record for record in list_case_records()}
CONSENT_STORE: dict[str, list[dict[str, Any]]] = {}
DOCUMENT_STORE: dict[str, list[dict[str, Any]]] = {}
AUDIT_LOGS: list[dict[str, Any]] = []
NOTIFICATION_STORE: list[dict[str, Any]] = []


def persist_case(case: dict[str, Any]) -> dict[str, Any]:
    CASE_STORE[case['case_id']] = case
    saved = save_case_record(case)
    CASE_STORE[case['case_id']] = saved
    return saved


def build_case_summary(case: dict[str, Any], case_id: str | None = None) -> dict[str, Any]:
    record_id = case_id or case.get('case_id')
    latest_department_check = None
    if case.get('department_checks'):
        latest_department_check = case['department_checks'][-1]
    return {
        'case_id': record_id,
        'status': case.get('status', 'DRAFT'),
        'service_id': case.get('service_id'),
        'applicant_name': case.get('applicant_name'),
        'decision': case.get('decision', {}),
        'latest_department_check': latest_department_check,
    }


@router.get('/cases/{case_id}')
def get_case(case_id: str):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')
    return case


@router.get('/cases/{case_id}/summary')
def get_case_summary(case_id: str):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')
    return build_case_summary(case, case_id=case_id)


@router.get('/cases/{case_id}/timeline')
def get_case_timeline(case_id: str):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    return {
        'case_id': case_id,
        'status': case.get('status', 'DRAFT'),
        'events': case.get('timeline', []),
    }


@router.get('/cases/{case_id}/notifications')
def get_case_notifications(case_id: str):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    notifications = []
    for event in case.get('timeline', []):
        notifications.append({
            'case_id': case_id,
            'event': event.get('event'),
            'message': f"Case status updated to {case.get('status', 'DRAFT')} via {event.get('event')}",
            'status': case.get('status', 'DRAFT'),
        })

    return {
        'case_id': case_id,
        'notifications': notifications,
    }


@router.get('/cases/{case_id}/audit')
def get_case_audit(case_id: str):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    records = [entry for entry in AUDIT_LOGS if entry.get('case_id') == case_id]
    return {
        'case_id': case_id,
        'records': records,
    }


@router.post('/cases/{case_id}/documents', status_code=status.HTTP_201_CREATED)
async def upload_case_document(
    case_id: str,
    request: Request,
    file: UploadFile,
    document_type: str = Form(default='supporting_document'),
):
    if case_id not in CASE_STORE:
        raise HTTPException(status_code=404, detail='Case not found')

    data = await file.read()
    document = {
        'case_id': case_id,
        'document_id': f'{case_id}-{len(DOCUMENT_STORE.get(case_id, [])) + 1}',
        'filename': file.filename or 'document.pdf',
        'document_type': document_type,
        'content_type': file.content_type or 'application/octet-stream',
        'size': len(data),
        'content_base64': base64.b64encode(data).decode('utf-8'),
        'uploaded_at': '2026-09-07T00:00:00Z',
    }
    DOCUMENT_STORE.setdefault(case_id, []).append(document)
    AUDIT_LOGS.append({
        'case_id': case_id,
        'actor': 'citizen',
        'action': 'DOCUMENT_UPLOADED',
        'resource': document['document_id'],
        'purpose': document['document_type'],
        'outcome': 'success',
        'correlation_id': request.headers.get('X-Correlation-ID', 'unknown'),
    })
    return document


@router.get('/cases/{case_id}/documents')
def list_case_documents(case_id: str):
    if case_id not in CASE_STORE:
        raise HTTPException(status_code=404, detail='Case not found')
    return {'case_id': case_id, 'documents': DOCUMENT_STORE.get(case_id, [])}


@router.post('/cases', status_code=status.HTTP_201_CREATED)
def create_case(request: Request, body: dict[str, Any]):
    case_id = generate_case_id()
    case = {
        'case_id': case_id,
        'service_id': body.get('service_id', 'scholarship'),
        'applicant_name': body.get('applicant_name', 'Unknown'),
        'status': 'DRAFT',
        'timeline': [],
        'department_checks': [],
        'decision': {},
        'review': {},
    }
    CASE_STORE[case_id] = case
    persist_case(case)
    AUDIT_LOGS.append({
        'case_id': case_id,
        'actor': 'citizen',
        'action': 'CASE_CREATED',
        'resource': case_id,
        'purpose': 'scholarship_eligibility',
        'outcome': 'success',
        'correlation_id': request.headers.get('X-Correlation-ID', 'unknown'),
    })
    return CASE_STORE[case_id]


@router.get('/cases')
def list_cases():
    return [build_case_summary(case, case_id=case.get('case_id')) for case in CASE_STORE.values()]


@router.post('/cases/{case_id}/consents', status_code=status.HTTP_201_CREATED)
def create_consent(case_id: str, request: Request, body: dict[str, Any]):
    if case_id not in CASE_STORE:
        raise HTTPException(status_code=404, detail='Case not found')
    entry = {
        'case_id': case_id,
        'purpose': body.get('purpose', 'scholarship_eligibility'),
        'attributes': body.get('attributes', ['income.status']),
        'decision': body.get('decision', 'approve'),
        'approved': body.get('decision') == 'approve',
    }
    CONSENT_STORE.setdefault(case_id, []).append(entry)
    AUDIT_LOGS.append({
        'case_id': case_id,
        'actor': 'citizen',
        'action': 'CONSENT_APPROVED',
        'resource': case_id,
        'purpose': entry['purpose'],
        'outcome': 'success',
        'correlation_id': request.headers.get('X-Correlation-ID', 'unknown'),
    })
    return entry


@router.post('/cases/{case_id}/data-requests')
def execute_data_request(case_id: str, request: Request, body: dict[str, Any]):
    if case_id not in CASE_STORE:
        raise HTTPException(status_code=404, detail='Case not found')
    consents = CONSENT_STORE.get(case_id, [])
    consent_approved = any(item.get('approved') for item in consents)
    if not consent_approved:
        raise HTTPException(status_code=403, detail='CONSENT_REQUIRED')

    attributes = body.get('attributes', ['income.status'])
    policy = evaluate_policy(purpose='scholarship_eligibility', attributes=attributes, consent_approved=True)
    if policy.decision != 'ALLOW':
        raise HTTPException(status_code=403, detail=policy.reason)

    income_data = fetch_income_data(attributes=attributes)
    canonical = canonicalize_income(income_data)
    CASE_STORE[case_id]['status'] = 'SUBMITTED'
    CASE_STORE[case_id]['timeline'].append({
        'event': 'DATA_RECEIVED',
        'payload': canonical,
    })
    persist_case(CASE_STORE[case_id])
    AUDIT_LOGS.append({
        'case_id': case_id,
        'actor': 'system',
        'action': 'DATA_REQUEST_EXECUTED',
        'resource': case_id,
        'purpose': 'scholarship_eligibility',
        'outcome': 'success',
        'correlation_id': request.headers.get('X-Correlation-ID', 'unknown'),
    })
    return {
        'status': 'completed',
        'case_id': case_id,
        'canonical': canonical,
        'provenance': canonical['provenance'],
    }


@router.post('/cases/{case_id}/department-checks')
def submit_department_check(case_id: str, request: Request, body: dict[str, Any]):
    if case_id not in CASE_STORE:
        raise HTTPException(status_code=404, detail='Case not found')

    department_id = body.get('department_id')
    service_id = body.get('service_id', 'scholarship')
    payload = body.get('payload', {})

    result = {
        'case_id': case_id,
        'department_id': department_id,
        'service_id': service_id,
        'status': 'verified' if payload.get('status') == 'employed' else 'eligible',
        'payload': payload,
    }

    CASE_STORE[case_id].setdefault('department_checks', []).append(result)
    CASE_STORE[case_id]['status'] = 'UNDER_REVIEW'
    CASE_STORE[case_id]['timeline'].append({
        'event': 'DEPARTMENT_CHECK',
        'department_id': department_id,
        'result': result['status'],
    })
    persist_case(CASE_STORE[case_id])
    AUDIT_LOGS.append({
        'case_id': case_id,
        'actor': 'system',
        'action': 'DEPARTMENT_CHECK_COMPLETED',
        'resource': department_id,
        'purpose': service_id,
        'outcome': 'success',
        'correlation_id': request.headers.get('X-Correlation-ID', 'unknown'),
    })
    return result


@router.post('/cases/{case_id}/decisions')
def set_case_decision(case_id: str, request: Request, body: dict[str, Any]):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    decision = {
        'case_id': case_id,
        'decision': body.get('decision', 'pending'),
        'reason': body.get('reason', ''),
        'recorded_at': '2026-09-07T00:00:00Z',
    }
    case['decision'] = decision
    case['status'] = 'DECISION_MADE'
    case['timeline'].append({
        'event': 'DECISION_MADE',
        'decision': decision['decision'],
        'reason': decision['reason'],
    })
    persist_case(case)
    AUDIT_LOGS.append({
        'case_id': case_id,
        'actor': 'officer',
        'action': 'CASE_DECISION_RECORDED',
        'resource': case_id,
        'purpose': 'decision_review',
        'outcome': 'success',
        'correlation_id': request.headers.get('X-Correlation-ID', 'unknown'),
        'timestamp': decision['recorded_at'],
    })

    from app.api.routes.decisions import DECISION_STORE
    if decision not in DECISION_STORE:
        DECISION_STORE.append(decision)
    return decision


@router.post('/cases/{case_id}/review')
def assign_case_review(case_id: str, body: dict[str, Any]):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    review = {
        'case_id': case_id,
        'assignee': body.get('assignee', 'unassigned'),
        'notes': body.get('notes', ''),
        'status': 'assigned',
    }
    case['review'] = review
    case['status'] = 'IN_REVIEW'
    case['timeline'].append({
        'event': 'CASE_ASSIGNED',
        'assignee': review['assignee'],
        'notes': review['notes'],
    })
    persist_case(case)
    return review


@router.post('/cases/{case_id}/reassign')
def reassign_case(case_id: str, body: dict[str, Any]):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    review = case.setdefault('review', {})
    review['assignee'] = body.get('assignee', review.get('assignee', 'unassigned'))
    review['notes'] = body.get('reason', review.get('notes', ''))
    review['status'] = 'assigned'
    case['status'] = 'IN_REVIEW'
    case['timeline'].append({
        'event': 'CASE_REASSIGNED',
        'assignee': review['assignee'],
        'reason': body.get('reason', ''),
    })
    persist_case(case)
    return {
        'case_id': case_id,
        'assignee': review['assignee'],
        'status': case['status'],
        'reason': body.get('reason', ''),
    }


@router.post('/cases/{case_id}/complete')
def complete_case(case_id: str, body: dict[str, Any]):
    case = CASE_STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    outcome = body.get('outcome', 'approved')
    case['status'] = 'COMPLETED'
    case['result'] = {
        'outcome': outcome,
        'notes': body.get('notes', ''),
    }
    case['timeline'].append({
        'event': 'CASE_COMPLETED',
        'outcome': outcome,
        'notes': body.get('notes', ''),
    })
    persist_case(case)
    return {
        'case_id': case_id,
        'status': 'COMPLETED',
        'outcome': outcome,
        'notes': body.get('notes', ''),
    }


@router.post('/notifications', status_code=status.HTTP_201_CREATED)
def create_notification(request: Request, body: dict[str, Any]):
    case_id = body.get('case_id')
    if not case_id:
        raise HTTPException(status_code=400, detail='case_id is required')

    notification = {
        'notification_id': f'notif-{len(NOTIFICATION_STORE) + 1}',
        'case_id': case_id,
        'channel': body.get('channel', 'email'),
        'recipient': body.get('recipient', 'unknown@example.com'),
        'message': body.get('message', 'Case updated.'),
        'status': 'queued',
        'created_at': '2026-09-07T00:00:00Z',
        'correlation_id': request.headers.get('X-Correlation-ID', 'unknown'),
    }
    NOTIFICATION_STORE.append(notification)
    return notification


@router.get('/notifications')
def list_notifications():
    notifications = []
    for case in CASE_STORE.values():
        for event in case.get('timeline', []):
            notifications.append({
                'case_id': case['case_id'],
                'event': event.get('event'),
                'message': f"Case status updated to {case.get('status', 'DRAFT')} via {event.get('event')}",
                'status': case.get('status', 'DRAFT'),
            })
    notifications.extend(NOTIFICATION_STORE)
    return {'notifications': notifications}


@router.get('/audit')
def get_audit(case_id: str | None = None):
    if case_id:
        return {'records': [item for item in AUDIT_LOGS if item['case_id'] == case_id]}
    return {'records': AUDIT_LOGS}
