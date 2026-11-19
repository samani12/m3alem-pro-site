import unittest
from m3si.marrakech import classify_query, opportunity_score, analyze_queries, build_service_keyword_map, generate_content_brief

class MarrakechSEOTests(unittest.TestCase):
    def test_local_commercial_query(self):
        r = classify_query("technicien climatisation Marrakech prix")
        self.assertTrue(r["local_intent"])
        self.assertTrue(r["transactional_intent"])
        self.assertIn("climatisation", r["services"])

    def test_arabic_local_query(self):
        r = classify_query("إصلاح مكيف في مراكش")
        self.assertTrue(r["local_intent"])
        self.assertIn("climatisation", r["services"])

    def test_score_is_bounded_and_explainable(self):
        r = opportunity_score("plombier Marrakech devis", 1200, 30, 0.01, 8)
        self.assertGreaterEqual(r["score"], 0)
        self.assertLessEqual(r["score"], 100)
        self.assertIn("marrakech_locality", r["factors"])
        self.assertEqual(r["recommended_page"], "plombier-marrakech.html")

    def test_local_commercial_beats_generic(self):
        local = opportunity_score("electricien Marrakech urgence", 1000, 20, 0.01, 7)
        generic = opportunity_score("electricite definition", 1000, 20, 0.01, 7)
        self.assertGreater(local["score"], generic["score"])

    def test_query_rows_sorted(self):
        rows = analyze_queries([
            {"query":"electricien Marrakech", "impressions":500, "clicks":4, "ctr":0.008, "position":9},
            {"query":"definition electricite", "impressions":20, "clicks":1, "ctr":0.05, "position":50},
        ])
        self.assertGreaterEqual(rows[0]["score"], rows[1]["score"])

    def test_keyword_map_uses_existing_service_pages(self):
        m = build_service_keyword_map([{"query":"plombier Marrakech", "impressions":100}])
        self.assertIn("plombier-marrakech.html", m)

    def test_content_brief_has_safety_rules(self):
        b = generate_content_brief("climatisation")
        self.assertEqual(b["target_page"], "climatisation-marrakech.html")
        self.assertTrue(b["guardrails"])

    def test_unknown_service_rejected(self):
        with self.assertRaises(ValueError):
            generate_content_brief("unknown")

if __name__ == "__main__":
    unittest.main()
