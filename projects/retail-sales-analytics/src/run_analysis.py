"""Run a reproducible sales analytics pipeline on the bundled synthetic dataset."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "sales.csv"
SCHEMA_FILE = ROOT / "sql" / "schema.sql"
OUTPUT_DIR = ROOT / "reports"
DATABASE_FILE = OUTPUT_DIR / "sales_analytics.db"

REQUIRED_COLUMNS = {
    "order_id", "order_date", "customer_id", "region", "category",
    "product", "quantity", "unit_price", "discount_pct",
}


def load_and_clean_data(path: Path) -> tuple[pd.DataFrame, dict[str, int]]:
    """Load CSV data, standardize fields and remove invalid/duplicate orders."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    raw = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    stats = {"rows_loaded": int(len(raw))}
    data = raw.copy()
    data["order_id"] = data["order_id"].astype("string").str.strip()
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    for column in ("quantity", "unit_price", "discount_pct"):
        data[column] = pd.to_numeric(data[column], errors="coerce")

    valid = (
        data["order_id"].notna()
        & data["order_id"].ne("")
        & data["order_date"].notna()
        & data["quantity"].gt(0)
        & data["unit_price"].ge(0)
    )
    stats["invalid_rows_removed"] = int((~valid).sum())
    data = data.loc[valid].copy()

    before_deduplication = len(data)
    data = data.drop_duplicates(subset=["order_id"], keep="first")
    stats["duplicate_rows_removed"] = int(before_deduplication - len(data))

    for column in ("customer_id", "region", "category", "product"):
        data[column] = data[column].astype("string").str.strip()
        data[column] = data[column].replace("", pd.NA).fillna("Unknown")

    data["discount_pct"] = data["discount_pct"].fillna(0)
    data = data.loc[data["discount_pct"].between(0, 100)].copy()
    data["order_date"] = data["order_date"].dt.strftime("%Y-%m-%d")
    data["net_revenue"] = (
        data["quantity"] * data["unit_price"] * (1 - data["discount_pct"] / 100)
    ).round(2)

    stats["clean_rows"] = int(len(data))
    return data, stats


def export_reports(connection: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Create report tables using SQL and export them as CSV files."""
    queries = {
        "monthly_revenue": """
            SELECT strftime('%Y-%m', order_date) AS month,
                   ROUND(SUM(net_revenue), 2) AS revenue,
                   COUNT(DISTINCT order_id) AS orders
            FROM sales
            GROUP BY month
            ORDER BY month
        """,
        "category_revenue": """
            SELECT category, ROUND(SUM(net_revenue), 2) AS revenue,
                   SUM(quantity) AS units_sold
            FROM sales
            GROUP BY category
            ORDER BY revenue DESC
        """,
        "top_products": """
            SELECT product, category, ROUND(SUM(net_revenue), 2) AS revenue,
                   SUM(quantity) AS units_sold
            FROM sales
            GROUP BY product, category
            ORDER BY revenue DESC
            LIMIT 5
        """,
        "region_revenue": """
            SELECT region, ROUND(SUM(net_revenue), 2) AS revenue,
                   COUNT(DISTINCT order_id) AS orders
            FROM sales
            GROUP BY region
            ORDER BY revenue DESC
        """,
    }

    reports: dict[str, pd.DataFrame] = {}
    for name, query in queries.items():
        frame = pd.read_sql_query(query, connection)
        frame.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)
        reports[name] = frame
    return reports


def create_monthly_chart(monthly: pd.DataFrame) -> Path:
    """Save a monthly revenue chart."""
    chart_path = OUTPUT_DIR / "monthly_revenue.png"
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(monthly["month"], monthly["revenue"])
    ax.set_title("Monthly Net Revenue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (currency units)")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
    return chart_path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_data, cleaning_stats = load_and_clean_data(DATA_FILE)

    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        clean_data.to_sql("sales", connection, if_exists="append", index=False)
        reports = export_reports(connection)
        kpis = pd.read_sql_query(
            """SELECT COUNT(DISTINCT order_id) AS total_orders,
                      ROUND(SUM(net_revenue), 2) AS total_revenue,
                      ROUND(AVG(net_revenue), 2) AS average_order_revenue
               FROM sales""",
            connection,
        ).iloc[0]

    chart_path = create_monthly_chart(reports["monthly_revenue"])
    print("\nSALES ANALYTICS SUMMARY")
    print("-" * 32)
    for name, value in cleaning_stats.items():
        print(f"{name.replace('_', ' ').title()}: {value}")
    print(f"Total orders: {int(kpis['total_orders'])}")
    print(f"Total net revenue: {kpis['total_revenue']:.2f}")
    print(f"Average revenue per order: {kpis['average_order_revenue']:.2f}")
    print(f"\nReports saved to: {OUTPUT_DIR}")
    print(f"Monthly chart: {chart_path.name}")
    print(f"SQLite database: {DATABASE_FILE.name}")


if __name__ == "__main__":
    main()
