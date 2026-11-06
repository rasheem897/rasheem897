DROP TABLE IF EXISTS sales;

CREATE TABLE sales (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    region TEXT NOT NULL,
    category TEXT NOT NULL,
    product TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_pct REAL NOT NULL CHECK (discount_pct BETWEEN 0 AND 100),
    net_revenue REAL NOT NULL CHECK (net_revenue >= 0)
);

CREATE INDEX idx_sales_order_date ON sales(order_date);
CREATE INDEX idx_sales_category ON sales(category);
CREATE INDEX idx_sales_region ON sales(region);
