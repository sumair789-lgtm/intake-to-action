"""
Approach 2: Auto-detect document type.

Pehla Gemini call sirf ye decide karta hai: "ye document invoice hai,
resume hai, ya lead/inquiry hai?" -- iske baad hi structure_data.py
sahi schema ke sath detailed extraction karta hai.

Ye do-step approach isliye better hai ek hi call mein sab guess karne se:
- Har type ka apna clean, focused schema milta hai
- Galat schema force karne se "hallucinated" fields nahi aatay
"""

import os
import json
from google import genai
from schema import ClassificationResult
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.6-flash"


def classify_document_type(raw_text: str) -> ClassificationResult:
    """
    Input: raw text (PDF se nikala hua)
    Output: ClassificationResult -- document_type + reason
    """
    schema_json = ClassificationResult.model_json_schema()

    prompt = f"""Neeche diya gaya text kisi document se nikala gaya hai.
Ye decide karo ye document kis type ka hai:

- "invoice"  -> agar isme vendor, amount, payment due jaisi cheezein hain
- "resume"   -> agar isme candidate ka experience, skills, education hai
- "lead"     -> agar ye ek inquiry/interest expressing message hai (customer kuch chahta hai)
- "unknown"  -> agar upar mein se koi bhi match nahi karta

TEXT:
---
{raw_text[:3000]}
---

SIRF JSON return karo, is schema ke mutabiq:
{json.dumps(schema_json, indent=2)}

JSON:"""

    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    raw_output = response.text.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]
    raw_output = raw_output.strip()

    try:
        data = json.loads(raw_output)
        return ClassificationResult(**data)
    except Exception as e:
        print(f"CLASSIFICATION FAILED: {e}")
        return ClassificationResult(document_type="unknown", reason="Classification failed")


if __name__ == "__main__":
    sample = "ABC Trading Co. Invoice #INV-001. Total Due: $500."
    result = classify_document_type(sample)
    print(result.model_dump_json(indent=2))
