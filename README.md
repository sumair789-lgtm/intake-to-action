# Intake-to-Action Service (Phase 1: Invoice Processing)

## Kaise chalayein

1. Dependencies install karo:
   pip install -r requirements.txt

2. Apni Gemini API key set karo (aistudio.google.com/apikey se banayi):

   Mac/Linux:
   export GEMINI_API_KEY="your-key-here"

   Windows PowerShell:
   $env:GEMINI_API_KEY="your-key-here"

   Windows CMD:
   set GEMINI_API_KEY=your-key-here

3. App chalao:
   python app.py

4. Browser mein kholo: http://localhost:5000

## Files kya karti hain

- schema.py        -> Kya fields extract karne hain (Pydantic schema)
- extract_text.py  -> PDF se raw text nikalna
- structure_data.py -> Gemini API se structured JSON banwana (FREE tier)
- database.py      -> Extracted data save karna (SQLite)
- actions.py       -> Alerts/notifications (amount threshold)
- app.py           -> Flask web app -- sab kuch jodta hai
- templates/dashboard.html -> Upload form + processed invoices table

## Test karna (LLM ke bina)

python3 -c "from schema import ExtractedInvoice; ..."
(structure_data.py chalane ke liye GEMINI_API_KEY zaroori hai)
