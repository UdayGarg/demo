import io
import pytest
from datetime import datetime, timezone
from app import app
from app.utils.storage import DatabaseConnection
import sqlite3

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def db():
    """Database fixture for tests"""
    db = DatabaseConnection()
    yield db
    # Clean up test database after each test
    import os
    if os.path.exists(db.db_path):
        os.remove(db.db_path)

class TestAnalyzeEndpoint:
    def test_analyze_endpoint_success(self, client):
        """Test successful document analysis"""
        data = {
            'document': (io.BytesIO(b"This is a hazard. Fire risk is evident."), 'test.txt')
        }
        response = client.post('/analyze', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'doc_id' in json_data
        assert 'revision' in json_data
        assert json_data['revision']['revision_number'] == 1
        assert 'timestamp' in json_data['revision']
        assert 'analysis' in json_data['revision']

    def test_analyze_empty_file(self, client):
        """Test submitting an empty file"""
        data = {
            'document': (io.BytesIO(b""), 'empty.txt')
        }
        response = client.post('/analyze', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        assert b'Could not read file content' in response.data

    def test_analyze_missing_file(self, client):
        """Test request without file"""
        response = client.post('/analyze', data={}, content_type='multipart/form-data')
        assert response.status_code == 400
        assert b'No file uploaded' in response.data

    def test_analyze_non_text_file(self, client):
        """Test submitting binary data"""
        data = {
            'document': (io.BytesIO(b'\x00\x01\x02\x03'), 'binary.dat')
        }
        response = client.post('/analyze', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

class TestHistoryEndpoint:
    def test_history_endpoint_invalid(self, client):
        """Test retrieving history for non-existent document"""
        response = client.get('/history/invalid-id')
        assert response.status_code == 404

    def test_history_endpoint_success(self, client):
        """Test successful history retrieval"""
        # First create a document
        data = {
            'document': (io.BytesIO(b"Test document content"), 'test.txt')
        }
        response = client.post('/analyze', data=data, content_type='multipart/form-data')
        doc_id = response.get_json()['doc_id']

        # Then get its history
        response = client.get(f'/history/{doc_id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'doc_id' in json_data
        assert 'revisions' in json_data
        assert len(json_data['revisions']) == 1

class TestReAuditEndpoint:
    def test_reaudit_success(self, client):
        """Test successful document re-audit"""
        # First create original document
        initial_data = {
            'document': (io.BytesIO(b"Initial content"), 'test.txt')
        }
        response = client.post('/analyze', data=initial_data, content_type='multipart/form-data')
        doc_id = response.get_json()['doc_id']

        # Then submit revision
        reaudit_data = {
            'doc_id': doc_id,
            'document': (io.BytesIO(b"Updated content"), 'test.txt')
        }
        response = client.post('/re_audit', data=reaudit_data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['revision']['revision_number'] == 2
        assert 'diff' in json_data['revision']

    def test_reaudit_missing_doc_id(self, client):
        """Test re-audit without document ID"""
        data = {
            'document': (io.BytesIO(b"Updated content"), 'test.txt')
        }
        response = client.post('/re_audit', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        assert b'Missing document ID' in response.data

    def test_reaudit_invalid_doc_id(self, client):
        """Test re-audit with invalid document ID"""
        data = {
            'doc_id': 'invalid-id',
            'document': (io.BytesIO(b"Updated content"), 'test.txt')
        }
        response = client.post('/re_audit', data=data, content_type='multipart/form-data')
        assert response.status_code == 404

    def test_reaudit_missing_file(self, client):
        """Test re-audit without file"""
        data = {
            'doc_id': 'some-id'
        }
        response = client.post('/re_audit', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        assert b'No file uploaded' in response.data

class TestDatabaseOperations:
    def test_store_revision(self, db):
        """Test storing revision in database"""
        doc_id = "test-doc-id"
        revision_data = {
            'revision_number': 1,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'original_text': "Test content",
            'analysis': {"test": "data"},
            'revised_document': "Revised content",
            'diff': None
        }
        
        # Store revision
        db.store_revision(doc_id, revision_data)
        

        with sqlite3.connect(db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM revisions WHERE doc_id = ?', (doc_id,))
            result = cursor.fetchone()
            assert result is not None
            assert result['revision_number'] == 1
            

    def test_get_revision_history(self, db):
        """Test retrieving revision history"""
        doc_id = "test-doc-id"
        revision_data = {
            'revision_number': 1,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'original_text': "Test content",
            'analysis': {"test": "data"},
            'revised_document': "Revised content",
            'diff': None
        }
        
        # Store revision
        db.store_revision(doc_id, revision_data)
        
        # Get history
        history = db.get_revision_history(doc_id)
        assert history is not None
        assert len(history) == 1
        assert history[0]['revision_number'] == 1

    def test_get_latest_revision_number(self, db):
        """Test getting latest revision number"""
        doc_id = "test-doc-id"
        for i in range(3):
            revision_data = {
                'revision_number': i + 1,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'original_text': f"Test content {i+1}",
                'analysis': {"test": "data"},
                'revised_document': f"Revised content {i+1}",
                'diff': None
            }
            db.store_revision(doc_id, revision_data)
        
        latest = db.get_latest_revision_number(doc_id)
        assert latest == 3

class TestIntegration:
    def test_full_document_lifecycle(self, client):
        """Test complete document lifecycle"""
        # 1. Create initial document
        initial_data = {
            'document': (io.BytesIO(b"Initial safety procedure"), 'test.txt')
        }
        response = client.post('/analyze', data=initial_data, content_type='multipart/form-data')
        assert response.status_code == 200
        doc_id = response.get_json()['doc_id']

        # 2. Verify history
        response = client.get(f'/history/{doc_id}')
        assert response.status_code == 200
        assert len(response.get_json()['revisions']) == 1

        # 3. Submit revision
        revision_data = {
            'doc_id': doc_id,
            'document': (io.BytesIO(b"Updated safety procedure"), 'test.txt')
        }
        response = client.post('/re_audit', data=revision_data, content_type='multipart/form-data')
        assert response.status_code == 200

        # 4. Verify updated history
        response = client.get(f'/history/{doc_id}')
        assert response.status_code == 200
        history = response.get_json()['revisions']
        assert len(history) == 2
        assert history[-1]['revision_number'] == 2