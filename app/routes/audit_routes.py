# app/routes/audit_routes.py
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.utils.analyzer import analyze_document, generate_revised_document, compute_diff
from app.utils.storage import store_revision, get_revision_history

audit_bp = Blueprint('audit_bp', __name__)

@audit_bp.route('/analyze', methods=['POST'])
def analyze():
    if 'document' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        content = file.read().decode('utf-8')
    except Exception:
        return jsonify({'error': 'Could not read file content'}), 400

    analysis_result = analyze_document(content)
    revised_document = generate_revised_document(content)
    doc_id = str(uuid.uuid4())
    revision_data = {
        'revision_number': 1,
        'timestamp': datetime.utcnow().isoformat(),
        'original_text': content,
        'analysis': analysis_result,
        'revised_document': revised_document,
        'diff': None
    }
    store_revision(doc_id, revision_data)
    return jsonify({'doc_id': doc_id, 'revision': revision_data})

@audit_bp.route('/history/<doc_id>', methods=['GET'])
def history(doc_id):
    history = get_revision_history(doc_id)
    if history is None:
        return jsonify({'error': 'Document ID not found'}), 404
    return jsonify({'doc_id': doc_id, 'revisions': history})

@audit_bp.route('/re_audit', methods=['POST'])
def re_audit():
    doc_id = request.form.get('doc_id')
    if not doc_id:
        return jsonify({'error': 'Missing document ID'}), 400

    if 'document' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        new_content = file.read().decode('utf-8')
    except Exception:
        return jsonify({'error': 'Could not read file content'}), 400

    history = get_revision_history(doc_id)
    if not history:
        return jsonify({'error': 'Document ID not found'}), 404

    last_revision = history[-1]
    old_text = last_revision['original_text']
    diff = compute_diff(old_text, new_content)

    analysis_result = analyze_document(new_content)
    revised_document = generate_revised_document(new_content)
    new_revision = {
        'revision_number': last_revision['revision_number'] + 1,
        'timestamp': datetime.utcnow().isoformat(),
        'original_text': new_content,
        'analysis': analysis_result,
        'revised_document': revised_document,
        'diff': diff
    }
    store_revision(doc_id, new_revision)
    return jsonify({'doc_id': doc_id, 'revision': new_revision})
