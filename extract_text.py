"""
Ye file PDF se raw text nikalti hai.
Agar PDF "digital" hai (text select ho sakta hai) -> seedha nikal lete hain.
Agar PDF scanned image hai (text nahi milta) -> abhi ke liye warning dete hain
(Phase 2 mein isme OCR fallback add karenge).
"""

import fitz  # PyMuPDF ka import naam 'fitz' hai


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Input: PDF file ka path
    Output: PDF ke andar ka poora text (saare pages combine karke)
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        full_text += page_text + "\n"

    doc.close()

    # Agar text bohot kam nikla (jaise < 20 characters), matlab ye scanned image PDF hai
    if len(full_text.strip()) < 20:
        print("WARNING: Bohot kam text mila -- ye scanned/image PDF ho sakta hai. "
              "OCR chahiye hoga (Phase 2 mein add karenge).")

    return full_text.strip()


# Quick test karne ke liye (khud chalane par)
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        text = extract_text_from_pdf(sys.argv[1])
        print("--- EXTRACTED TEXT ---")
        print(text)
    else:
        print("Usage: python extract_text.py <path_to_pdf>")
