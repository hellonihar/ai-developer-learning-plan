"""Generate example policy PDFs from source text files using PyMuPDF."""

from pathlib import Path
import fitz

EXAMPLES_DIR = Path(__file__).parent
SOURCES = [
    ("policy_01_commercial_liability.txt", "Commercial General Liability Insurance Policy"),
    ("policy_02_data_protection.txt", "Data Protection and Privacy Policy"),
    ("policy_03_code_of_conduct.txt", "Employee Code of Conduct"),
]


def txt_to_pdf(txt_path: Path, title: str) -> Path:
    pdf_path = txt_path.with_suffix(".pdf")
    raw = txt_path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    doc = fitz.open()
    page = doc.new_page()

    page.insert_text((72, 80), title, fontsize=16)

    y = 120
    for line in lines:
        if y > 730:
            page = doc.new_page()
            y = 72
        if line.strip():
            page.insert_text((72, y), line, fontsize=9)
        y += 11

    doc.save(pdf_path)
    size = Path(pdf_path).stat().st_size
    pages = doc.page_count
    doc.close()
    print(f"  {pdf_path.name}  ({pages} pages, {size:,} bytes)")
    return pdf_path


if __name__ == "__main__":
    for filename, title in SOURCES:
        txt_path = EXAMPLES_DIR / filename
        print(f"Processing {filename}...")
        txt_to_pdf(txt_path, title)
    print("Done.")
