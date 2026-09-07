import unittest

from src.query_parser import parse_query
from src.search_engine import _build_search_query, search


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


if __name__ == "__main__":
    unittest.main()
