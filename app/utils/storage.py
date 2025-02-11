import sqlite3
import json
from datetime import datetime
import os

class DatabaseConnection:
    def __init__(self):
        # Store database in the app directory
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'audit.db')
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Read schema from file
            schema_path = os.path.join(os.path.dirname(__file__), '..', 'migrations', 'schema.sql')
            with open(schema_path, 'r') as schema_file:
                schema = schema_file.read()
            # Execute schema
            conn.executescript(schema)

def store_revision(doc_id, revision_data):
    """Store a new revision in the database"""
    db = DatabaseConnection()
    
    with sqlite3.connect(db.db_path) as conn:
        conn.row_factory = sqlite3.Row
        
        # First, ensure the document exists
        conn.execute('INSERT OR IGNORE INTO documents (doc_id) VALUES (?)', (doc_id,))
        
        # Then store the revision
        conn.execute('''
            INSERT INTO revisions 
            (doc_id, revision_number, timestamp, original_text, analysis, revised_document, diff)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            doc_id,
            revision_data['revision_number'],
            revision_data['timestamp'],
            revision_data['original_text'],
            json.dumps(revision_data['analysis']),  # Convert dict to JSON string
            revision_data['revised_document'],
            revision_data['diff']
        ))

def get_revision_history(doc_id):
    """Retrieve the revision history for a document"""
    db = DatabaseConnection()
    
    with sqlite3.connect(db.db_path) as conn:
        conn.row_factory = sqlite3.Row
        
        # Check if document exists
        doc = conn.execute('SELECT doc_id FROM documents WHERE doc_id = ?', (doc_id,)).fetchone()
        if not doc:
            return None
            
        # Get all revisions
        cursor = conn.execute('''
            SELECT revision_number, timestamp, original_text, analysis, revised_document, diff
            FROM revisions 
            WHERE doc_id = ?
            ORDER BY revision_number
        ''', (doc_id,))
        
        revisions = []
        for row in cursor:
            revision = dict(row)
            # Parse JSON string back to dict
            revision['analysis'] = json.loads(revision['analysis'])
            revisions.append(revision)
            
        return revisions

def get_latest_revision_number(doc_id):
    """Get the latest revision number for a document"""
    db = DatabaseConnection()
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.execute('''
            SELECT MAX(revision_number) as last_rev
            FROM revisions
            WHERE doc_id = ?
        ''', (doc_id,))
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0