"""
Ye file ab GENERIC hai -- kaunsa schema use karna hai, wo
document_type ke hisab se decide hota hai (schema.SCHEMA_MAP se).
"""

import os
import json
from google import genai
from schema import SCHEMA_MAP
from pydantic import ValidationError, BaseModel
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.6-flash"


def build_extraction_prompt(raw_text: str, schema_class) -> str:
    schema_json = schema_class.model_json_schema()

    return f"""Neeche di gayi raw text se structured data nikalo.

RAW TEXT:
---
{raw_text}
---

Neeche diye gaye JSON schema ke EXACT mutabiq ek JSON object return karo.
SIRF JSON return karo -- koi extra text ya markdown fences nahi.
Agar koi field text mein nahi milta, null/default rakho -- khud se mat banao.

SCHEMA:
{json.dumps(schema_json, indent=2)}

JSON:"""


def extract_structured(raw_text: str, document_type: str) -> BaseModel:
    """
    Input: raw text + document_type ("invoice"/"resume"/"lead")
    Output: schema_map ke mutabiq validated Pydantic object
    """
    schema_class = SCHEMA_MAP.get(document_type)
    if schema_class is None:
        raise ValueError(f"Unknown document_type: {document_type}")

    prompt = build_extraction_prompt(raw_text, schema_class)
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    raw_output = response.text.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]
    raw_output = raw_output.strip()

    try:
        data_dict = json.loads(raw_output)
        return schema_class(**data_dict)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"EXTRACTION FAILED: {e}")
        print(f"RAW OUTPUT WAS: {raw_output}")
        # Fallback -- generic flagged object banao
        fallback_data = {"confidence_flag": False}
        if document_type == "invoice":
            fallback_data.update({"vendor_name": "UNKNOWN - REVIEW NEEDED", "total_amount": 0.0})
        elif document_type == "resume":
            fallback_data.update({"candidate_name": "UNKNOWN - REVIEW NEEDED"})
        elif document_type == "lead":
            fallback_data.update({"contact_name": "UNKNOWN - REVIEW NEEDED", "interest": "unclear"})
        return schema_class(**fallback_data)
