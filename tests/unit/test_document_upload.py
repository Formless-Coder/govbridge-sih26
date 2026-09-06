from fastapi.testclient import TestClient

from app.main import app


def test_case_documents_can_be_uploaded_and_listed():
    client = TestClient(app)
    created = client.post(
        '/api/v1/cases',
        json={'service_id': 'scholarship', 'applicant_name': 'Upload User'},
    )
    case_id = created.json()['case_id']

    response = client.post(
        f'/api/v1/cases/{case_id}/documents',
        files={'file': ('income-proof.pdf', b'%PDF-1.4 fake pdf', 'application/pdf')},
        data={'document_type': 'income_certificate'},
    )

    assert response.status_code == 201
    body = response.json()
    assert body['filename'] == 'income-proof.pdf'
    assert body['document_type'] == 'income_certificate'

    listing = client.get(f'/api/v1/cases/{case_id}/documents')
    assert listing.status_code == 200
    docs = listing.json()['documents']
    assert any(doc['filename'] == 'income-proof.pdf' for doc in docs)
