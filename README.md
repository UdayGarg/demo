# Safety Document Audit System

A Flask-based RESTful API service that provides automated safety document analysis and revision tracking using OpenAI's GPT models. The system maintains a complete audit trail of document revisions in a SQLite database and provides detailed safety recommendations.

## Technical Architecture

### Core Components
- **Flask Backend**: REST API implementation with Blueprint architecture
- **OpenAI Integration**: GPT-4o for document analysis and recommendations
- **SQLite Database**: Persistent storage with document versioning
- **CORS Support**: Cross-origin resource sharing enabled for API access

### Database Schema
The system uses a SQLite database with two primary tables:

#### Documents Table
```sql
CREATE TABLE documents (
    doc_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Revisions Table
```sql
CREATE TABLE revisions (
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
```

## Installation

### Prerequisites
- Python 3.12 or higher
- uv (tool from astral - pip install uv)
- OpenAI API key
- Flask and dependencies

### Setup Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create and activate a virtual environment:
```bash
uv run hello.py
uv sync
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

4. Initialize the database:
```bash
mkdir app/migrations
cp schema.sql app/migrations/
```

5. run the server on localHost:
```bash
uv run -m app.main
```

## API Endpoints

### 1. Analyze Document
**Endpoint**: `POST /analyze`  
**Purpose**: Upload and analyze a new safety document  
**Request Format**: Multipart form data with 'document' file  
**Response Format**:
```json
{
    "doc_id": "uuid-string",
    "revision": {
        "revision_number": 1,
        "timestamp": "ISO-8601-timestamp",
        "original_text": "document-content",
        "analysis": {
            "detected_hazards": ["..."],
            "compliance_issues": ["..."],
            "regulatory_comments": {},
            "accident_incidents": ["..."]
        },
        "revised_document": "revised-content",
        "diff": null
    }
}
```

### 2. Get Document History
**Endpoint**: `GET /history/<doc_id>`  
**Purpose**: Retrieve revision history for a document  
**Response Format**:
```json
{
    "doc_id": "uuid-string",
    "revisions": [
        {
            "revision_number": 1,
            "timestamp": "ISO-8601-timestamp",
            "original_text": "document-content",
            "analysis": {},
            "revised_document": "revised-content",
            "diff": "unified-diff-format"
        }
    ]
}
```

### 3. Re-audit Document
**Endpoint**: `POST /re_audit`  
**Purpose**: Submit a new version of an existing document for analysis  
**Request Format**: Multipart form data with:
- 'document' file
- 'doc_id' field

## Technical Implementation Details

### Document Analysis
The system uses OpenAI's GPT-4o model for document analysis with the following features:

1. **Hazard Detection**: Identifies potential safety hazards in the document
2. **Compliance Analysis**: Checks for regulatory compliance issues
3. **Recommendation Generation**: Provides specific safety recommendations
4. **Diff Generation**: Creates unified diffs between document versions

### Database Operations
- Uses SQLite with connection pooling
- Implements JSON serialization for analysis data
- Maintains referential integrity between documents and revisions
- Includes indexes for optimized query performance

### Error Handling
The API implements comprehensive error handling for:
- File upload failures
- Database operations
- OpenAI API interactions
- JSON parsing errors
- Invalid document IDs

## Development and Testing

### Running the Application
```bash
python -m app.main
```

### Running Tests
```bash
pytest tests/
```

### Configuration
Configuration settings in `app/config.py`:
- `DEBUG`: Enable/disable debug mode
- `PORT`: Application port (default: 5000)

## Security Considerations

1. **API Security**:
   - Input validation on all endpoints
   - File type checking for uploads
   - Size limits on document uploads

2. **Database Security**:
   - Parameterized queries to prevent SQL injection
   - Transaction management for data integrity
   - Proper error handling and logging

## Performance Optimization

1. **Database Optimizations**:
   - Indexed queries for frequent operations
   - Connection pooling
   - Efficient JSON storage and retrieval

2. **API Response Optimization**:
   - Pagination for large result sets
   - Efficient diff generation
   - Proper HTTP status codes and headers

## Limitations and Considerations

1. **OpenAI API Dependencies**:
   - Rate limiting considerations
   - Token limit constraints
   - Cost implications for analysis

2. **Database Scalability**:
   - SQLite limitations for concurrent access
   - Consider migration path to PostgreSQL for higher load

3. **File type**:
   - Currently limited to plaintext, can be modified 
