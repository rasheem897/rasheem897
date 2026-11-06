-- Revenue by month
SELECT substr(order_date, 1, 7) AS month,
       ROUND(SUM(net_revenue), 2) AS revenue,
       COUNT(*) AS order_count
FROM orders
GROUP BY month
ORDER BY month;

-- Revenue by customer region
SELECT c.region, ROUND(SUM(o.net_revenue), 2) AS revenue,
       COUNT(*) AS order_count
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
GROUP BY c.region
ORDER BY revenue DESC;

-- Revenue by customer segment
SELECT c.segment, ROUND(SUM(o.net_revenue), 2) AS revenue,
       COUNT(*) AS order_count
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
GROUP BY c.segment
ORDER BY revenue DESC;

-- Top products by net revenue
SELECT product, ROUND(SUM(net_revenue), 2) AS revenue,
       SUM(quantity) AS units_sold
FROM orders
GROUP BY product
ORDER BY revenue DESC;

-- Customers with highest lifetime revenue
SELECT c.customer_id, c.customer_name,
       ROUND(SUM(o.net_revenue), 2) AS lifetime_revenue
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY lifetime_revenue DESC
LIMIT 10;
