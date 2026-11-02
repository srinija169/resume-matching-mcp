import unittest
from utils.matching import score_resume, rank_candidates


class MatchingTests(unittest.TestCase):
    def test_keyword_score(self):
        result = score_resume("Python developer SQL", "Python and SQL developer")
        self.assertEqual(result["score"], 100.0)

    def test_rank_order(self):
        resumes = [
            {"filename": "low.txt", "status": "success", "text": "Java"},
            {"filename": "high.txt", "status": "success", "text": "Python SQL"},
        ]
        ranked = rank_candidates("Python SQL", resumes)
        self.assertEqual(ranked[0]["filename"], "high.txt")


if __name__ == "__main__":
    unittest.main()
