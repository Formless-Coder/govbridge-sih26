from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any


EVENT_STORE: dict[str, dict[str, Any]] = {}
IDEMPOTENCY_INDEX: dict[str, str] = {}
RETRY_LOGS: list[dict[str, Any]] = []
DLQ_LOGS: list[dict[str, Any]] = []


def _timestamp() -> str:
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


def publish_event(*, event_type: str, aggregate_type: str, aggregate_id: str, payload: dict[str, Any], idempotency_key: str | None = None, metadata: dict[str, Any] | None = None) -> tuple[dict[str, Any], bool]:
    if idempotency_key and idempotency_key in IDEMPOTENCY_INDEX:
        event_id = IDEMPOTENCY_INDEX[idempotency_key]
        return EVENT_STORE[event_id], True

    event_id = f'evt-{uuid.uuid4().hex[:12]}'
    event = {
        'event_id': event_id,
        'event_type': event_type,
        'aggregate_type': aggregate_type,
        'aggregate_id': aggregate_id,
        'idempotency_key': idempotency_key,
        'payload': payload or {},
        'metadata': metadata or {},
        'status': 'queued',
        'attempts': 0,
        'retry_count': 0,
        'created_at': _timestamp(),
        'processed_at': None,
        'last_error': None,
    }
    EVENT_STORE[event_id] = event
    if idempotency_key:
        IDEMPOTENCY_INDEX[idempotency_key] = event_id
    return event, False


def process_event(*, event_id: str, result: str, reason: str | None = None) -> dict[str, Any]:
    event = EVENT_STORE.get(event_id)
    if event is None:
        raise KeyError(f'Unknown event: {event_id}')

    event['attempts'] += 1
    if result == 'success':
        event['status'] = 'processed'
        event['processed_at'] = _timestamp()
        event['last_error'] = None
        return {
            'event_id': event_id,
            'status': 'processed',
            'result': 'success',
            'processed_at': event['processed_at'],
        }

    event['status'] = 'retry'
    event['retry_count'] += 1
    event['last_error'] = reason or 'processing_failed'
    retry_record = {
        'event_id': event_id,
        'event_type': event['event_type'],
        'aggregate_type': event['aggregate_type'],
        'aggregate_id': event['aggregate_id'],
        'reason': event['last_error'],
        'attempt': event['attempts'],
        'retry_count': event['retry_count'],
        'created_at': _timestamp(),
    }
    RETRY_LOGS.append(retry_record)

    if event['retry_count'] >= 3:
        event['status'] = 'dead_letter'
        dlq_record = {
            **retry_record,
            'status': 'dead_letter',
            'dead_lettered_at': _timestamp(),
        }
        DLQ_LOGS.append(dlq_record)
        return {
            'event_id': event_id,
            'status': 'dead_letter',
            'result': 'failure',
            'reason': event['last_error'],
            'retry_count': event['retry_count'],
        }

    return {
        'event_id': event_id,
        'status': 'retry',
        'result': 'failure',
        'reason': event['last_error'],
        'retry_count': event['retry_count'],
    }


def get_retry_records() -> list[dict[str, Any]]:
    return list(RETRY_LOGS)


def get_dead_letter_records() -> list[dict[str, Any]]:
    return list(DLQ_LOGS)
