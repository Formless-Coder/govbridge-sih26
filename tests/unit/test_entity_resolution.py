from fastapi.testclient import TestClient

from app.main import app


def test_entity_resolution_groups_duplicate_person_records():
    client = TestClient(app)
    payload = {
        'records': [
            {
                'id': 'citizen-001',
                'name': 'Aman Giri',
                'dob': '1990-01-01',
                'phone': '9876543210',
                'email': 'aman@example.com',
            },
            {
                'id': 'citizen-002',
                'name': 'Aman G.',
                'dob': '1990-01-01',
                'phone': '9876543210',
                'email': 'aman.giri@example.com',
            },
            {
                'id': 'citizen-003',
                'name': 'Neha Rao',
                'dob': '1995-03-12',
                'phone': '9123456780',
                'email': 'neha@example.com',
            },
        ]
    }

    response = client.post('/api/v1/entities/resolve', json=payload)

    assert response.status_code == 200
    body = response.json()
    assert 'resolved_entities' in body
    assert 'duplicate_groups' in body
    assert any(len(group['record_ids']) >= 2 for group in body['duplicate_groups'])
    assert any(entity['status'] == 'duplicate_candidate' for entity in body['resolved_entities'])
