-- app/migrations/schema.sql

-- Documents table stores basic document information
CREATE TABLE IF NOT EXISTS documents (
    doc_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Revisions table stores all document revisions
CREATE TABLE IF NOT EXISTS revisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT,
    revision_number INTEGER,
    timestamp TIMESTAMP,
    original_text TEXT,
    analysis JSON,
    revised_document TEXT,
    diff TEXT,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_revisions_doc_id ON revisions(doc_id);
