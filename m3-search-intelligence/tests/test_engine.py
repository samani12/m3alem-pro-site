import unittest
from m3si.engine import normalize_url, score_opportunity

class EngineTests(unittest.TestCase):
    def test_normalize_removes_fragment(self):
        self.assertEqual(normalize_url("https://example.com/a#section"), "https://example.com/a")

    def test_rejects_non_http_scheme(self):
        with self.assertRaises(ValueError):
            normalize_url("file:///etc/passwd")

    def test_score_is_bounded(self):
        for impressions, ctr, position in [(0,0,0),(100000,0,5),(500,0.2,100)]:
            score = score_opportunity(impressions, ctr, position)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_high_impression_low_ctr_opportunity(self):
        score = score_opportunity(5000, 0.01, 8)
        self.assertGreater(score, score_opportunity(50, 0.01, 8))

if __name__ == "__main__":
    unittest.main()
