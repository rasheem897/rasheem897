-- Monthly revenue and order count
SELECT strftime('%Y-%m', order_date) AS month,
       ROUND(SUM(net_revenue), 2) AS revenue,
       COUNT(DISTINCT order_id) AS orders
FROM sales
GROUP BY month
ORDER BY month;

-- Revenue by product category
SELECT category,
       ROUND(SUM(net_revenue), 2) AS revenue,
       SUM(quantity) AS units_sold
FROM sales
GROUP BY category
ORDER BY revenue DESC;

-- Top five products by net revenue
SELECT product, category,
       ROUND(SUM(net_revenue), 2) AS revenue,
       SUM(quantity) AS units_sold
FROM sales
GROUP BY product, category
ORDER BY revenue DESC
LIMIT 5;

-- Revenue by region
SELECT region,
       ROUND(SUM(net_revenue), 2) AS revenue,
       COUNT(DISTINCT order_id) AS orders
FROM sales
GROUP BY region
ORDER BY revenue DESC;
