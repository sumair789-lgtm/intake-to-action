"""
Ye file define karti hai ke har document TYPE se kya extract karna hai.
Ab hum 3 types support karte hain: invoice, resume, lead.
Classification (kaunsa type hai) classify.py mein hoti hai.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal


# ---------- Shared ----------

DocumentType = Literal["invoice", "resume", "lead", "unknown"]


class ClassificationResult(BaseModel):
    """Gemini ka pehla output -- ye document kis type ka hai"""
    document_type: DocumentType
    reason: str = Field(description="Ek line mein kyun ye type decide kiya")


# ---------- Invoice ----------

class LineItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: Optional[float] = None
    total: Optional[float] = None


class ExtractedInvoice(BaseModel):
    vendor_name: str
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    total_amount: float
    currency: str = "USD"
    line_items: list[LineItem] = Field(default_factory=list)
    confidence_flag: bool = True


# ---------- Resume ----------

class ExtractedResume(BaseModel):
    candidate_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    current_role: Optional[str] = Field(default=None, description="Latest job title mentioned")
    years_experience: Optional[float] = Field(default=None, description="Total years of experience, estimate if needed")
    skills: list[str] = Field(default_factory=list)
    confidence_flag: bool = True


# ---------- Lead ----------

class ExtractedLead(BaseModel):
    contact_name: str
    company: Optional[str] = None
    interest: str = Field(description="What they are asking about / interested in")
    budget: Optional[float] = None
    currency: str = "USD"
    timeline: Optional[str] = Field(default=None, description="When they need it, if mentioned")
    confidence_flag: bool = True


# Schema registry -- classify.py ka result isi se map hota hai
SCHEMA_MAP = {
    "invoice": ExtractedInvoice,
    "resume": ExtractedResume,
    "lead": ExtractedLead,
}
