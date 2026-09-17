# Intake-to-Action Service

A document intake pipeline that reads any PDF -- invoice, resume, or lead
inquiry -- automatically detects what type of document it is, extracts
structured data from it, and files it into a searchable ledger.

No manual sorting, no manual data entry.

## How it works

```
PDF upload
    |
    v
extract_text.py    -- pulls raw text from the PDF
    |
    v
classify.py        -- Gemini decides: invoice / resume / lead / unknown
    |
    v
structure_data.py  -- Gemini extracts fields using the matching schema
    |
    v
schema.py           -- Pydantic validates the extracted fields
    |
    v
database.py         -- saved to SQLite (generic table, all types fit)
    |
    v
actions.py           -- alerts if amount is high / confidence is low
    |
    v
dashboard.html        -- ledger view, filterable by document type
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a free Gemini API key

- Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- Sign in with a personal Google account (not a managed/organization account)
- Click "Create API Key" -- no billing required for the free tier

### 3. Add your key to a `.env` file

Create a file named `.env` in the project root (same folder as `app.py`):

```
GEMINI_API_KEY=your-key-here
```

No quotes, no spaces around `=`. This file is already in `.gitignore` --
it will never be pushed to GitHub.

### 4. Run the app

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

## What each file does

| File | Role |
|---|---|
| `schema.py` | Pydantic schemas for each document type (Invoice, Resume, Lead) + the classification schema |
| `extract_text.py` | Pulls raw text out of an uploaded PDF |
| `classify.py` | First Gemini call -- decides which document type this is |
| `structure_data.py` | Second Gemini call -- extracts fields using the matching schema, with a fallback if extraction fails |
| `database.py` | Generic SQLite table that stores all three document types, mapping their fields into shared columns |
| `actions.py` | Notification logic -- high-amount alerts for invoices, low-confidence flags for any type |
| `app.py` | Flask app that wires the whole pipeline together and serves the dashboard |
| `templates/dashboard.html` | Ledger-style dashboard with drag-and-drop upload, type filters, and per-type contextual columns |

## Supported document types

| Type | What's extracted | "Context" column shows | "Metric" column shows |
|---|---|---|---|
| Invoice | vendor, invoice #, dates, line items, total | due date | total amount |
| Resume | candidate name, role, email, skills, experience | email | years of experience (falls back to skills count if missing) |
| Lead | contact name, company, interest, budget, timeline | timeline | budget |

Anything that doesn't match one of these is saved as `unknown` and flagged
for manual review, instead of being forced into the wrong schema.

## Testing without calling the API

The schema, database, and actions layers can be tested without a live
Gemini key:

```bash
python3 -c "
from schema import ExtractedInvoice
from database import save_record, get_all_records
inv = ExtractedInvoice(vendor_name='Test Co', total_amount=500.0)
save_record('invoice', inv, 'test.pdf')
print(get_all_records())
"
```

Running `classify.py` or `structure_data.py` directly requires a valid
`GEMINI_API_KEY` in your `.env` file, since those make real API calls.

## Notes

- Free tier Gemini models occasionally return a `503 UNAVAILABLE` error
  under high demand -- this is temporary on Google's side; just retry.
- `invoices.db` and anything in `uploads/` are git-ignored by default, so
  test data doesn't get pushed to GitHub.