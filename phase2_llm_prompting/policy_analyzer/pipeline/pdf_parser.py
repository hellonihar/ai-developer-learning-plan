import fitz


def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = "\n\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()
