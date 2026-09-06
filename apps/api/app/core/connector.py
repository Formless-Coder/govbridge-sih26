from __future__ import annotations

from typing import Any


INCOME_MOCK_DATA = {
    'income': {
        'status': 'employed',
        'monthly_income': 45000,
        'source_reference': 'APP-001',
    }
}

CONNECTOR_REGISTRY: list[dict[str, Any]] = [
    {
        'id': 'income-http',
        'name': 'income-http',
        'protocol': 'http',
        'category': 'department',
        'service_id': 'scholarship',
        'status': 'active',
        'base_url': 'https://mock-gov.local/income',
        'description': 'HTTP-based income verification connector for employment and earnings checks.',
        'attributes': ['income.status', 'income.monthly_income'],
    },
    {
        'id': 'scholarship-events',
        'name': 'scholarship-events',
        'protocol': 'message',
        'category': 'event',
        'service_id': 'scholarship',
        'status': 'active',
        'queue': 'scholarship.applications',
        'description': 'Message-based connector that publishes scholarship lifecycle events to a broker.',
        'attributes': ['scholarship_eligibility', 'application.status'],
    },
]


def list_connectors(*, protocol: str | None = None) -> list[dict[str, Any]]:
    connectors = CONNECTOR_REGISTRY
    if protocol:
        connectors = [item for item in connectors if item.get('protocol') == protocol]
    return [dict(item) for item in connectors]


def fetch_income_data(*, attributes: list[str]) -> dict[str, Any]:
    data = INCOME_MOCK_DATA.copy()
    filtered = {}
    if 'income.status' in attributes:
        filtered['income'] = {'status': data['income']['status']}
    return filtered


def canonicalize_income(payload: dict[str, Any]) -> dict[str, Any]:
    income = payload.get('income', {})
    return {
        'income': {
            'status': income.get('status', 'unknown'),
        },
        'provenance': {
            'source_system': 'income_rest_mock',
            'source_identifier': 'APP-001',
            'timestamp': '2026-09-06T00:00:00Z',
            'schema_version': '1.0',
            'transformation_context': 'income_rest_mock_to_canonical',
        },
    }
