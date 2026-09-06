from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


REQUEST_COUNTER = {'total_requests': 0}
LOGS: list[dict[str, Any]] = []
TRACES: list[dict[str, Any]] = []


def _timestamp() -> str:
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


def record_request(*, method: str, path: str, status_code: int) -> None:
    REQUEST_COUNTER['total_requests'] += 1
    LOGS.append({
        'timestamp': _timestamp(),
        'level': 'INFO',
        'message': f'{method} {path}',
        'status_code': status_code,
    })
    TRACES.append({
        'timestamp': _timestamp(),
        'method': method,
        'path': path,
        'status_code': status_code,
    })


def get_observability_summary() -> dict[str, Any]:
    return {
        'metrics': {
            'total_requests': REQUEST_COUNTER['total_requests'],
            'status_codes': {'2xx': sum(1 for trace in TRACES if 200 <= trace['status_code'] < 300), '4xx': sum(1 for trace in TRACES if 400 <= trace['status_code'] < 500), '5xx': sum(1 for trace in TRACES if 500 <= trace['status_code'] < 600)},
        },
        'logs': LOGS,
        'traces': TRACES,
    }
