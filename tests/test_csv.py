import unittest
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from io import StringIO


# Assuming the original script is named csv_processor.py
from main import (
    process_numeric, process_string, filter_table, aggregate,
    validate_where, validate_aggregate, AGG_ALLOWED, AGG_RE, main
)

CSV_PATH = Path(__file__).resolve().parent.parent / "processing_csv"


class TestValidate(unittest.TestCase):
    def test_validate_where_ok(self):
        validate_where("price>500")
        validate_where("brand=apple")
        validate_where("rating<4.9")

    def test_validate_where_bad_operator(self):
        with patch("sys.stdout", new_callable=StringIO):
            with self.assertRaises(SystemExit):
                validate_where("price<>=500")

    def test_validate_aggregate_ok(self):
        for func in AGG_ALLOWED:
            validate_aggregate(f"price={func}")

    def test_validate_aggregate_bad(self):
        with patch("sys.stdout", new_callable=StringIO):
            with self.assertRaises(SystemExit):
                validate_aggregate("price=test")

class TestProcessingHelpers(unittest.TestCase):
    def test_process_numeric(self):
        self.assertTrue(process_numeric("10", "5", ">"))
        self.assertFalse(process_numeric(3, "10", ">"))

        self.assertTrue(process_numeric("3", "10", "<"))
        self.assertFalse(process_numeric("10", "5", "<"))

    def test_process_string_eq(self):
        self.assertTrue(process_string("Apple", "'app'", "="))
        self.assertFalse(process_string("Samsung", "'apple'", "="))

    def test_agg_re(self):
        # Регулярка должна принимать только допустимые агрегаторы
        self.assertIsNotNone(AGG_RE.match("price=sum"))
        self.assertIsNone(AGG_RE.match("price=median"))


class TestFilterAndAggregate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import csv
        with open('../products.csv', encoding="utf-8") as f:
            cls.rows = list(csv.DictReader(f))

    def test_filter_numeric(self):
        res = filter_table(self.rows, "price>500")
        self.assertEqual(len(res), 2)
        self.assertTrue(all(float(r["price"]) > 500 for r in res))

    def test_filter_string(self):
        res = filter_table(self.rows, "brand='xiaomi'")
        self.assertEqual(len(res), 2)
        self.assertTrue(all(r["brand"].lower() == "xiaomi" for r in res))

    def test_aggregate_avg(self):
        res = aggregate(self.rows, "price=avg")
        self.assertIn("avg", res.lower())
        self.assertIn("674", res)

