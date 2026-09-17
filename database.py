"""
Ek hi generic table -- kyunki invoice/resume/lead teeno ke fields
alag hain, hum unko "primary_label", "secondary_label", "metric_value"
jaisi generic columns mein map karte hain, aur poora extracted data
JSON string ki tarah bhi save karte hain (kabhi zaroorat pare to).
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class RecordEntry(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    doc_type = Column(String)          # "invoice" / "resume" / "lead" / "unknown"
    primary_label = Column(String)     # vendor_name / candidate_name / contact_name
    secondary_label = Column(String, nullable=True)  # invoice_number / current_role / company
    date_field = Column(String, nullable=True)       # invoice_date (sirf invoice ke liye)
    metric_value = Column(Float, nullable=True)       # total_amount / years_experience / budget
    metric_unit = Column(String, nullable=True)        # currency / "yrs" / currency
    full_data_json = Column(Text)      # poora extracted object, JSON string ki tarah
    confidence_flag = Column(Boolean, default=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    source_filename = Column(String, nullable=True)


engine = create_engine("sqlite:///invoices.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def save_record(doc_type: str, extracted_obj, source_filename: str = None) -> int:
    """
    doc_type ke hisab se extracted_obj ke fields ko generic columns mein map karta hai.
    """
    data = extracted_obj.model_dump()

    if doc_type == "invoice":
        primary = data.get("vendor_name")
        secondary = data.get("invoice_number")
        # "Context" column -- due date agar mile, warna invoice date
        date_field = data.get("due_date") or data.get("invoice_date")
        metric_value = data.get("total_amount")
        metric_unit = data.get("currency")
    elif doc_type == "resume":
        primary = data.get("candidate_name")
        secondary = data.get("current_role")
        # "Context" column -- resume ke liye date ka koi matlab nahi, email zyada useful hai
        date_field = data.get("email")
        metric_value = data.get("years_experience")
        metric_unit = "yrs exp"
        # Fallback: agar experience na mile, skills count dikhao (bilkul khaali chhodne se behtar)
        if metric_value is None:
            skills = data.get("skills") or []
            if skills:
                metric_value = float(len(skills))
                metric_unit = "skills"
    elif doc_type == "lead":
        primary = data.get("contact_name")
        secondary = data.get("company")
        # "Context" column -- lead ke liye timeline zyada useful hai date se
        date_field = data.get("timeline")
        metric_value = data.get("budget")
        metric_unit = data.get("currency")
    else:
        primary = "Unclassified document"
        secondary = None
        date_field = None
        metric_value = None
        metric_unit = None

    session = Session()
    record = RecordEntry(
        doc_type=doc_type,
        primary_label=primary,
        secondary_label=secondary,
        date_field=date_field,
        metric_value=metric_value,
        metric_unit=metric_unit,
        full_data_json=json.dumps(data),
        confidence_flag=data.get("confidence_flag", True),
        source_filename=source_filename,
    )
    session.add(record)
    session.commit()
    record_id = record.id
    session.close()
    return record_id


def get_all_records(doc_type_filter: str = None):
    session = Session()
    query = session.query(RecordEntry)
    if doc_type_filter and doc_type_filter != "all":
        query = query.filter(RecordEntry.doc_type == doc_type_filter)
    records = query.order_by(RecordEntry.processed_at.desc()).all()
    session.close()
    return records
