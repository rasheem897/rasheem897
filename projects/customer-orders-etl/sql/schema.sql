PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS order_enriched;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    region TEXT NOT NULL,
    segment TEXT NOT NULL
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    product TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_pct REAL NOT NULL CHECK (discount_pct BETWEEN 0 AND 100),
    net_revenue REAL NOT NULL CHECK (net_revenue >= 0),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_product ON orders(product);

CREATE VIEW order_enriched AS
SELECT o.order_id, o.order_date, o.product, o.quantity, o.unit_price,
       o.discount_pct, o.net_revenue, c.customer_id, c.customer_name,
       c.region, c.segment
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id;
