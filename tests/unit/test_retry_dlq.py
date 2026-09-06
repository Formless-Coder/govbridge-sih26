from fastapi.testclient import TestClient

from app.main import app


def test_event_processing_moves_failed_messages_to_dead_letter_queue():
    client = TestClient(app)

    queued = client.post(
        '/api/v1/events',
        json={
            'event_type': 'CASE_SYNC_FAILED',
            'aggregate_type': 'case',
            'aggregate_id': 'GOV-2026-000099',
            'idempotency_key': 'evt-sync-failed-099',
            'payload': {'status': 'FAILED'},
        },
    )
    event_id = queued.json()['event_id']

    for _ in range(3):
        response = client.post(
            f'/api/v1/events/{event_id}/process',
            json={'result': 'failure', 'reason': 'upstream_timeout'},
        )

    assert response.status_code == 200
    assert response.json()['status'] == 'dead_letter'

    dlq = client.get('/api/v1/events/dlq')
    assert dlq.status_code == 200
    assert any(item['event_id'] == event_id for item in dlq.json()['records'])
