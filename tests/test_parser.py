import tempfile
import unittest
from pathlib import Path
from utils.resume_parser import extract_resume_text


class ParserTests(unittest.TestCase):
    def test_txt_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "candidate.txt"
            path.write_text("Python developer", encoding="utf-8")
            self.assertEqual(extract_resume_text(path), "Python developer")


if __name__ == "__main__":
    unittest.main()
