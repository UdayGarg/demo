# app/utils/storage.py
revision_history = {}

def store_revision(doc_id, revision_data):
    if doc_id not in revision_history:
        revision_history[doc_id] = []
    revision_history[doc_id].append(revision_data)

def get_revision_history(doc_id):
    return revision_history.get(doc_id)
