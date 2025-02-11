# app/utils/analyzer.py

import os
import json
from openai import OpenAI
import difflib

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_document(text):
    """
    Uses OpenAI GPT to analyze the provided safety document.
    Returns a structured analysis of hazards, compliance issues, and recommendations.
    """
    prompt = """
You are a safety procedure auditor. Analyze the following safety document and extract the requested information.
Format your response as a JSON object with exactly these keys:
{
    "detected_hazards": ["list of hazard sentences"],
    "compliance_issues": ["list of compliance issue sentences"],
    "regulatory_comments": {"standard": "guideline"},
    "accident_incidents": ["list of historical incidents"],
    "original_text": "the complete document"
}
Ensure that each sentence is complete and properly quoted.

Document:
"""
    # Add the document text
    prompt += text

    # Add explicit formatting instructions
    prompt += """

Return ONLY valid JSON that matches the exact format shown above. Do not include any additional explanation or text outside the JSON structure."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",  # Using the latest model which is better at JSON
            messages=[
                {"role": "system", "content": "You are a safety procedure auditor that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # Enforce JSON response
            temperature=0,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse JSON: {str(e)}",
            "raw_response": content
        }
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "raw_response": None
        }

def generate_revised_document(text):
    """
    Uses OpenAI GPT to generate a revised version of the safety document with recommendations.
    """
    prompt = """
As a safety procedure auditor, revise the following document:
1. Identify each sentence that mentions a hazard
2. Add a specific recommendation after each hazard
3. Keep all other content unchanged
4. Format recommendations as "Recommendation: [specific action]"

Document:
"""
    prompt += text
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a safety procedure auditor focusing on clear, actionable recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating revision: {str(e)}"

def compute_diff(old_text, new_text):
    """
    Computes a unified diff between the old and new document versions.
    """
    try:
        diff = difflib.unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            fromfile='Previous Version',
            tofile='New Version',
            lineterm=''
        )
        return "\n".join(list(diff))
    except Exception as e:
        return f"Error computing diff: {str(e)}"