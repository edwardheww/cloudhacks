import unittest
from datetime import date

from src.query_parser import parse_query
from src.search_engine import _build_search_query, _get_match_reasons, search


class SearchEngineTests(unittest.TestCase):
    def test_empty_query_returns_no_results_without_loading_model(self):
        self.assertEqual(search("   "), [])

    def test_query_builder_adds_structured_filters(self):
        parsed = parse_query("cheap Thai food near Clementi this weekend")
        sql, parameters = _build_search_query(parsed, "[0.1,0.2]", 5)

        self.assertIn("LOWER(deals.cuisine)", sql)
        self.assertIn("LOWER(deals.location)", sql)
        self.assertIn("LOWER(deals.price)", sql)
        self.assertIn("deals.expiry_date", sql)
        self.assertEqual(parameters[-1], 5)

    def test_match_reasons_only_include_actual_deal_matches(self):
        parsed = parse_query("cheap Thai food near Clementi this weekend", reference_date=date(2026, 9, 7))
        deal = {
            "cuisine": "Thai",
            "location": "Tampines",
            "price": "cheap",
            "start_date": date(2026, 9, 1),
            "expiry_date": date(2026, 9, 30),
        }

        self.assertEqual(
            _get_match_reasons(deal, parsed),
            ["Thai cuisine", "Budget-friendly", "Available this weekend"],
        )

    def test_match_reasons_do_not_copy_query_reasons_to_unmatched_deal(self):
        parsed = parse_query("Thai food this weekend near Clementi", reference_date=date(2026, 9, 7))
        deal = {
            "cuisine": "Western",
            "location": "Tampines",
            "price": "moderate",
            "start_date": date(2026, 9, 20),
            "expiry_date": date(2026, 9, 30),
        }

        self.assertEqual(_get_match_reasons(deal, parsed), [])


if __name__ == "__main__":
    unittest.main()
