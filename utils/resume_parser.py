"""Small, replaceable resume text extraction helpers."""
from pathlib import Path


def extract_resume_text(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    if suffix == ".docx":
        from docx import Document
        document = Document(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

    raise ValueError(f"Unsupported file type: {suffix}")
