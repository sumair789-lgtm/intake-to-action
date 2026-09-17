"""
Main Flask app -- pipeline ab do-step hai:
1. classify_document_type() -- pehle decide karo ye kya hai
2. extract_structured() -- phir sahi schema se extract karo
"""

from flask import Flask, request, render_template, redirect, url_for
import os

from extract_text import extract_text_from_pdf
from classify import classify_document_type
from structure_data import extract_structured
from database import save_record, get_all_records
from actions import check_and_notify

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def dashboard():
    doc_filter = request.args.get("type", "all")
    records = get_all_records(doc_filter)
    return render_template("dashboard.html", records=records, active_filter=doc_filter)


@app.route("/upload", methods=["POST"])
def upload():
    if "invoice_file" not in request.files:
        return "Koi file upload nahi hui", 400

    file = request.files["invoice_file"]
    if file.filename == "":
        return "File select nahi ki", 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # --- Poora pipeline ---
    raw_text = extract_text_from_pdf(filepath)
    classification = classify_document_type(raw_text)
    structured = extract_structured(raw_text, classification.document_type)
    record_id = save_record(classification.document_type, structured, source_filename=file.filename)
    check_and_notify(classification.document_type, structured, record_id)
    # ----------------------

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
