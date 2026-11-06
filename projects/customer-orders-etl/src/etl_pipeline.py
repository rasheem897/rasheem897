"""A small, reproducible customer and order ETL pipeline."""
from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SQL_DIR = ROOT / "sql"
REPORTS_DIR = ROOT / "reports"
CUSTOMERS_FILE = DATA_DIR / "customers.csv"
ORDERS_FILE = DATA_DIR / "orders.csv"
SCHEMA_FILE = SQL_DIR / "schema.sql"
DATABASE_FILE = REPORTS_DIR / "customer_orders.db"

CUSTOMER_COLUMNS = {"customer_id", "customer_name", "region", "segment"}
ORDER_COLUMNS = {
    "order_id", "order_date", "customer_id", "product", "quantity",
    "unit_price", "discount_pct",
}

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{label} CSV is missing columns: {sorted(missing)}")


def transform_customers(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Normalize customer data and retain one row per valid customer ID."""
    _require_columns(frame, CUSTOMER_COLUMNS, "Customer")
    data = frame.copy()
    counts: dict[str, int] = {"customer_rows_loaded": int(len(data))}

    for column in CUSTOMER_COLUMNS:
        data[column] = data[column].astype("string").str.strip()

    valid = data["customer_id"].notna() & data["customer_id"].ne("")
    valid &= data["customer_name"].notna() & data["customer_name"].ne("")
    counts["invalid_customer_rows"] = int((~valid).sum())
    data = data.loc[valid].copy()

    before = len(data)
    data = data.drop_duplicates(subset=["customer_id"], keep="first")
    counts["duplicate_customer_rows"] = int(before - len(data))

    for column in ("region", "segment"):
        data[column] = data[column].replace("", pd.NA).fillna("Unknown")

    counts["customers_loaded"] = int(len(data))
    return data.reset_index(drop=True), counts


def transform_orders(
    frame: pd.DataFrame, valid_customer_ids: set[str]
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Validate orders, remove duplicates and reject unknown customer IDs."""
    _require_columns(frame, ORDER_COLUMNS, "Order")
    data = frame.copy()
    counts: dict[str, int] = {"order_rows_loaded": int(len(data))}

    for column in ("order_id", "customer_id", "product"):
        data[column] = data[column].astype("string").str.strip()
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    for column in ("quantity", "unit_price", "discount_pct"):
        data[column] = pd.to_numeric(data[column], errors="coerce")

    valid = (
        data["order_id"].notna() & data["order_id"].ne("")
        & data["customer_id"].notna() & data["customer_id"].ne("")
        & data["product"].notna() & data["product"].ne("")
        & data["order_date"].notna()
        & data["quantity"].gt(0)
        & data["unit_price"].ge(0)
        & data["discount_pct"].between(0, 100)
    )
    counts["invalid_order_rows"] = int((~valid).sum())
    data = data.loc[valid].copy()

    before = len(data)
    data = data.drop_duplicates(subset=["order_id"], keep="first")
    counts["duplicate_order_rows"] = int(before - len(data))

    known_customer = data["customer_id"].isin(valid_customer_ids)
    counts["unknown_customer_rows"] = int((~known_customer).sum())
    data = data.loc[known_customer].copy()

    data["order_date"] = data["order_date"].dt.strftime("%Y-%m-%d")
    data["net_revenue"] = (
        data["quantity"] * data["unit_price"]
        * (1 - data["discount_pct"] / 100)
    ).round(2)
    data["quantity"] = data["quantity"].astype(int)
    counts["orders_loaded"] = int(len(data))
    return data.reset_index(drop=True), counts


def _export_sql_reports(
    connection: sqlite3.Connection, output_dir: Path
) -> dict[str, pd.DataFrame]:
    """Execute SQL aggregations and export report CSVs."""
    queries = {
        "monthly_revenue": """
            SELECT substr(order_date, 1, 7) AS month,
                   ROUND(SUM(net_revenue), 2) AS revenue,
                   COUNT(*) AS order_count
            FROM orders GROUP BY month ORDER BY month
        """,
        "region_revenue": """
            SELECT c.region, ROUND(SUM(o.net_revenue), 2) AS revenue,
                   COUNT(*) AS order_count
            FROM orders o JOIN customers c ON c.customer_id = o.customer_id
            GROUP BY c.region ORDER BY revenue DESC
        """,
        "segment_revenue": """
            SELECT c.segment, ROUND(SUM(o.net_revenue), 2) AS revenue,
                   COUNT(*) AS order_count
            FROM orders o JOIN customers c ON c.customer_id = o.customer_id
            GROUP BY c.segment ORDER BY revenue DESC
        """,
        "product_revenue": """
            SELECT product, ROUND(SUM(net_revenue), 2) AS revenue,
                   SUM(quantity) AS units_sold
            FROM orders GROUP BY product ORDER BY revenue DESC
        """,
        "top_customers": """
            SELECT c.customer_id, c.customer_name,
                   ROUND(SUM(o.net_revenue), 2) AS lifetime_revenue
            FROM customers c JOIN orders o ON o.customer_id = c.customer_id
            GROUP BY c.customer_id, c.customer_name
            ORDER BY lifetime_revenue DESC LIMIT 10
        """,
    }
    reports: dict[str, pd.DataFrame] = {}
    for name, query in queries.items():
        report = pd.read_sql_query(query, connection)
        report.to_csv(output_dir / f"{name}.csv", index=False)
        reports[name] = report
    return reports


def run_pipeline(
    customers_path: Path = CUSTOMERS_FILE,
    orders_path: Path = ORDERS_FILE,
    database_path: Path = DATABASE_FILE,
    schema_path: Path = SCHEMA_FILE,
    reports_dir: Path = REPORTS_DIR,
) -> dict[str, Any]:
    """Run extract, transform, load and report stages; return run metadata."""
    for required_file in (customers_path, orders_path, schema_path):
        if not required_file.exists():
            raise FileNotFoundError(f"Required input file not found: {required_file}")

    reports_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Extracting customer and order CSV files")
    customer_raw = pd.read_csv(customers_path, dtype="string")
    order_raw = pd.read_csv(orders_path, dtype="string")

    customers, customer_stats = transform_customers(customer_raw)
    orders, order_stats = transform_orders(
        order_raw, set(customers["customer_id"].astype(str))
    )

    LOGGER.info("Loading %d customers and %d orders into SQLite", len(customers), len(orders))
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        customers.to_sql("customers", connection, if_exists="append", index=False)
        orders.to_sql("orders", connection, if_exists="append", index=False)
        reports = _export_sql_reports(connection, reports_dir)
        kpi = pd.read_sql_query(
            "SELECT COUNT(*) AS total_orders, ROUND(SUM(net_revenue), 2) AS total_revenue "
            "FROM orders", connection,
        ).iloc[0]

    quality = {**customer_stats, **order_stats}
    quality["rows_rejected_total"] = (
        quality["invalid_order_rows"] + quality["duplicate_order_rows"]
        + quality["unknown_customer_rows"]
    )
    quality["orders_loaded"] = int(kpi["total_orders"])
    quality["total_net_revenue"] = float(kpi["total_revenue"] or 0)
    (reports_dir / "data_quality.json").write_text(
        json.dumps(quality, indent=2), encoding="utf-8"
    )

    LOGGER.info("ETL completed: %s", json.dumps(quality, sort_keys=True))
    return {
        "quality": quality,
        "database_path": str(database_path),
        "report_files": [f"{name}.csv" for name in reports],
    }


def main() -> None:
    result = run_pipeline()
    print("\nETL RUN SUMMARY")
    print("-" * 32)
    for key, value in result["quality"].items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print(f"\nSQLite database: {result['database_path']}")
    print(f"CSV reports: {', '.join(result['report_files'])}")


if __name__ == "__main__":
    main()
