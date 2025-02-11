# app/utils/analyzer.py
import re
import difflib

HAZARD_KEYWORDS = ['hazard', 'danger', 'risk', 'unsafe', 'violation', 'fire', 'fall', 'electrical']
REGULATORY_RULES = {
    'electrical': "According to IEC 60364, electrical installations must adhere to strict standards.",
    'fire': "NFPA 101 requires building design to include robust fire safety measures.",
    'hazard': "OSHA guidelines mandate mitigation of recognized hazards."
}
ACCIDENT_HISTORY = [
    {"keyword": "fire", "incident": "Warehouse fire due to non-compliant safety measures."},
    {"keyword": "fall", "incident": "Worker injury from fall in an unguarded area."},
    {"keyword": "electrical", "incident": "Electrical shock incident linked to outdated wiring."}
]

def analyze_document(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    detected_hazards = []
    compliance_issues = []
    regulatory_comments = {}
    accident_incidents = []

    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in HAZARD_KEYWORDS):
            detected_hazards.append(sentence.strip())
            for keyword, guideline in REGULATORY_RULES.items():
                if keyword in sentence_lower:
                    regulatory_comments.setdefault(keyword, guideline)
        if 'non-compliant' in sentence_lower or 'violation' in sentence_lower:
            compliance_issues.append(sentence.strip())

    for record in ACCIDENT_HISTORY:
        if record["keyword"] in text.lower():
            accident_incidents.append(record["incident"])

    return {
        'detected_hazards': detected_hazards,
        'compliance_issues': compliance_issues,
        'regulatory_comments': regulatory_comments,
        'accident_incidents': accident_incidents,
        'original_text': text
    }

def generate_revised_document(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    revised_sentences = []
    for sentence in sentences:
        revised = sentence
        if any(keyword in sentence.lower() for keyword in HAZARD_KEYWORDS):
            revised += " [Recommendation: Review this procedure and implement risk mitigation measures.]"
        revised_sentences.append(revised)
    return " ".join(revised_sentences)

def compute_diff(old_text, new_text):
    diff = difflib.unified_diff(
        old_text.splitlines(),
        new_text.splitlines(),
        fromfile='Previous Version',
        tofile='New Version',
        lineterm=''
    )
    return "\n".join(list(diff))
