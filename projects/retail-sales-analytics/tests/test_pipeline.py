"""Unit tests for the sample data cleaning pipeline."""
import unittest
from pathlib import Path

from src.run_analysis import DATA_FILE, load_and_clean_data


class SalesPipelineTests(unittest.TestCase):
    def test_sample_data_cleaning_counts(self) -> None:
        cleaned, stats = load_and_clean_data(DATA_FILE)

        self.assertEqual(stats["rows_loaded"], 50)
        self.assertEqual(stats["invalid_rows_removed"], 1)
        self.assertEqual(stats["duplicate_rows_removed"], 1)
        self.assertEqual(stats["clean_rows"], 48)
        self.assertEqual(len(cleaned), 48)
        self.assertTrue(cleaned["order_id"].is_unique)
        self.assertTrue(cleaned["net_revenue"].ge(0).all())

    def test_revenue_calculation(self) -> None:
        cleaned, _ = load_and_clean_data(DATA_FILE)
        sample = cleaned.loc[cleaned["order_id"].eq("ORD0001")].iloc[0]
        expected = round(3 * 1299 * (1 - 5 / 100), 2)
        self.assertEqual(sample["net_revenue"], expected)

    def test_missing_file_raises_clear_error(self) -> None:
        missing_path = DATA_FILE.parent / "does-not-exist.csv"
        with self.assertRaises(FileNotFoundError):
            load_and_clean_data(missing_path)


if __name__ == "__main__":
    unittest.main()
