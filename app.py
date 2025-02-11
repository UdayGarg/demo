# app.py
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Define some keywords for our demo analysis
HAZARD_KEYWORDS = ['hazard', 'danger', 'risk', 'unsafe', 'violation']
REGULATORY_KEYWORDS = ['compliance', 'regulation', 'standard', 'protocol']

def analyze_document(text):
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    detected_hazards = []
    compliance_issues = []
    
    for sentence in sentences:
        # Check for hazard keywords
        for keyword in HAZARD_KEYWORDS:
            if keyword.lower() in sentence.lower():
                detected_hazards.append(sentence.strip())
                break
        # Check for phrases suggesting compliance issues
        if 'non-compliant' in sentence.lower() or 'violation' in sentence.lower():
            compliance_issues.append(sentence.strip())
    
    return {
        'detected_hazards': detected_hazards,
        'compliance_issues': compliance_issues,
        'original_text': text
    }

def generate_revised_document(text):
    # Simple revision: append recommendations to sentences with hazards
    sentences = re.split(r'(?<=[.!?]) +', text)
    revised_sentences = []
    
    for sentence in sentences:
        revised = sentence
        if any(keyword in sentence.lower() for keyword in HAZARD_KEYWORDS):
            revised += " [Recommendation: Review this procedure and implement risk mitigation measures.]"
        revised_sentences.append(revised)
        
    return " ".join(revised_sentences)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'document' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        # For this demo, we assume a plain text file
        content = file.read().decode('utf-8')
    except Exception as e:
        return jsonify({'error': 'Could not read file content'}), 400

    analysis_result = analyze_document(content)
    revised_document = generate_revised_document(content)
    analysis_result['revised_document'] = revised_document
    return jsonify(analysis_result)

if __name__ == '__main__':
    app.run(debug=True)

