# tests/test_audit.py
import io
import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_analyze_endpoint(client):
    data = {
        'document': (io.BytesIO(b"This is a hazard. Fire risk is evident."), 'test.txt')
    }
    response = client.post('/analyze', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'doc_id' in json_data
    assert 'revision' in json_data

def test_history_endpoint_invalid(client):
    response = client.get('/history/invalid-id')
    assert response.status_code == 404

