from fastapi.testclient import TestClient

from app.main import app


def test_event_publish_is_idempotent_and_queued():
    client = TestClient(app)
    payload = {
        'event_type': 'CASE_CREATED',
        'aggregate_type': 'case',
        'aggregate_id': 'GOV-2026-000001',
        'idempotency_key': 'evt-case-created-101',
        'payload': {'service_id': 'scholarship', 'applicant_name': 'Aman Giri'},
    }

    response = client.post('/api/v1/events', json=payload)
    assert response.status_code == 202
    body = response.json()
    assert body['status'] == 'queued'
    assert body['event_type'] == 'CASE_CREATED'
    assert body['aggregate_id'] == 'GOV-2026-000001'

    duplicate = client.post('/api/v1/events', json=payload)
    assert duplicate.status_code == 200
    duplicate_body = duplicate.json()
    assert duplicate_body['duplicate'] is True
    assert duplicate_body['event_id'] == body['event_id']


def test_event_processing_marks_processed_and_retries_failed_messages():
    client = TestClient(app)

    queued = client.post(
        '/api/v1/events',
        json={
            'event_type': 'CASE_UPDATED',
            'aggregate_type': 'case',
            'aggregate_id': 'GOV-2026-000002',
            'idempotency_key': 'evt-case-updated-201',
            'payload': {'status': 'SUBMITTED'},
        },
    )
    event_id = queued.json()['event_id']

    processed = client.post(f'/api/v1/events/{event_id}/process', json={'result': 'success'})
    assert processed.status_code == 200
    assert processed.json()['status'] == 'processed'

    failed = client.post(
        '/api/v1/events',
        json={
            'event_type': 'CASE_UPDATED',
            'aggregate_type': 'case',
            'aggregate_id': 'GOV-2026-000003',
            'idempotency_key': 'evt-case-updated-301',
            'payload': {'status': 'RETRY'},
            'metadata': {'retry': True},
        },
    )
    failed_event_id = failed.json()['event_id']

    retry_response = client.post(
        f'/api/v1/events/{failed_event_id}/process',
        json={'result': 'failure', 'reason': 'upstream_timeout'},
    )
    assert retry_response.status_code == 200
    assert retry_response.json()['status'] == 'retry'

    retries = client.get('/api/v1/events/retries')
    assert retries.status_code == 200
    assert any(record['event_id'] == failed_event_id for record in retries.json()['records'])
