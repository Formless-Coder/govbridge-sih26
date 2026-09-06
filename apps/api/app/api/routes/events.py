from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.events import EVENT_STORE, get_dead_letter_records, get_retry_records, process_event, publish_event

router = APIRouter(tags=['events'])


@router.post('/events')
def publish_events(body: dict[str, Any]):
    missing = [field for field in ['event_type', 'aggregate_type', 'aggregate_id'] if not body.get(field)]
    if missing:
        raise HTTPException(status_code=400, detail=f'Missing required fields: {missing}')

    event, duplicate = publish_event(
        event_type=body['event_type'],
        aggregate_type=body['aggregate_type'],
        aggregate_id=body['aggregate_id'],
        payload=body.get('payload', {}),
        idempotency_key=body.get('idempotency_key'),
        metadata=body.get('metadata', {}),
    )

    response = {
        'event_id': event['event_id'],
        'status': event['status'],
        'duplicate': duplicate,
        'event_type': event['event_type'],
        'aggregate_type': event['aggregate_type'],
        'aggregate_id': event['aggregate_id'],
        'idempotency_key': event.get('idempotency_key'),
    }

    if duplicate:
        return JSONResponse(status_code=200, content=response)
    return JSONResponse(status_code=202, content=response)


@router.post('/events/{event_id}/process')
def process_event_route(event_id: str, body: dict[str, Any]):
    if event_id not in EVENT_STORE:
        raise HTTPException(status_code=404, detail='Event not found')

    result = body.get('result', 'failure')
    reason = body.get('reason')
    processed = process_event(event_id=event_id, result=result, reason=reason)
    return processed


@router.get('/events/retries')
def get_event_retries():
    return {'records': get_retry_records()}


@router.get('/events/dlq')
def get_event_dlq():
    return {'records': get_dead_letter_records()}
