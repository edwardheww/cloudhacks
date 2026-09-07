from datetime import date
import unittest

from src.query_parser import parse_query


class QueryParserTests(unittest.TestCase):
    def test_parses_all_mvp_filters(self):
        parsed = parse_query(
            "cheap Thai food near Clementi this weekend",
            reference_date=date(2026, 9, 7),
        )

        self.assertEqual(parsed.cuisine, "Thai")
        self.assertEqual(parsed.location, "Clementi")
        self.assertEqual(parsed.price, "cheap")
        self.assertEqual(parsed.date_range.start, date(2026, 9, 12))
        self.assertEqual(parsed.date_range.end, date(2026, 9, 13))

    def test_parses_tomorrow(self):
        parsed = parse_query("coffee deals tomorrow", reference_date=date(2026, 9, 7))

        self.assertEqual(parsed.date_range.start, date(2026, 9, 8))
        self.assertEqual(parsed.date_range.end, date(2026, 9, 8))

    def test_leaves_unknown_filters_empty(self):
        parsed = parse_query("surprise me", reference_date=date(2026, 9, 7))

        self.assertIsNone(parsed.cuisine)
        self.assertIsNone(parsed.location)
        self.assertIsNone(parsed.price)
        self.assertIsNone(parsed.date_range)


if __name__ == "__main__":
    unittest.main()
