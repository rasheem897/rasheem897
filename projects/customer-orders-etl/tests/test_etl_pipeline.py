"""Tests for extraction, transformation and loading behavior."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.etl_pipeline import CUSTOMERS_FILE, ORDERS_FILE, SCHEMA_FILE, run_pipeline


class EtlPipelineTests(unittest.TestCase):
    def test_sample_pipeline_counts_and_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            result = run_pipeline(
                customers_path=CUSTOMERS_FILE,
                orders_path=ORDERS_FILE,
                database_path=temp / "warehouse.db",
                schema_path=SCHEMA_FILE,
                reports_dir=temp / "reports",
            )

            quality = result["quality"]
            self.assertEqual(quality["customer_rows_loaded"], 14)
            self.assertEqual(quality["invalid_customer_rows"], 1)
            self.assertEqual(quality["duplicate_customer_rows"], 1)
            self.assertEqual(quality["customers_loaded"], 12)
            self.assertEqual(quality["order_rows_loaded"], 36)
            self.assertEqual(quality["invalid_order_rows"], 4)
            self.assertEqual(quality["duplicate_order_rows"], 1)
            self.assertEqual(quality["unknown_customer_rows"], 1)
            self.assertEqual(quality["orders_loaded"], 30)

            with sqlite3.connect(temp / "warehouse.db") as connection:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0], 12
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 30
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM order_enriched").fetchone()[0], 30
                )

            self.assertTrue((temp / "reports" / "monthly_revenue.csv").exists())
            self.assertTrue((temp / "reports" / "data_quality.json").exists())
            saved_quality = json.loads(
                (temp / "reports" / "data_quality.json").read_text()
            )
            self.assertEqual(saved_quality["orders_loaded"], 30)

    def test_missing_source_file_raises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            with self.assertRaises(FileNotFoundError):
                run_pipeline(
                    customers_path=temp / "missing.csv",
                    orders_path=ORDERS_FILE,
                    database_path=temp / "warehouse.db",
                    schema_path=SCHEMA_FILE,
                    reports_dir=temp / "reports",
                )


if __name__ == "__main__":
    unittest.main()
