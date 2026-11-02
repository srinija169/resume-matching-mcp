
import tempfile
import unittest
from pathlib import Path

from docx import Document
from reportlab.pdfgen import canvas

from utils.resume_parser import extract_resume_text


class ParserTests(unittest.TestCase):

    def test_txt_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "candidate.txt"
            path.write_text("Python developer", encoding="utf-8")

            result = extract_resume_text(path)

            self.assertIn("Python developer", result)

    def test_docx_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "candidate.docx"

            document = Document()
            document.add_paragraph("Python developer with SQL experience")
            document.save(path)

            result = extract_resume_text(path)

            self.assertIn("Python developer", result)
            self.assertIn("SQL", result)

    def test_pdf_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "candidate.pdf"

            pdf = canvas.Canvas(str(path))
            pdf.drawString(100, 750, "Python developer with API experience")
            pdf.save()

            result = extract_resume_text(path)

            self.assertIn("Python developer", result)
            self.assertIn("API", result)

    def test_unsupported_file_type(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "candidate.xlsx"
            path.write_text("Some content", encoding="utf-8")

            with self.assertRaises(ValueError):
                extract_resume_text(path)


if __name__ == "__main__":
    unittest.main()
