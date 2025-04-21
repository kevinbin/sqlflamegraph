#!/bin/bash

# 从dsn文件读取数据库连接信息
DSN="mysql://msandbox:msandbox@127.0.0.1:8037/test"

# 提取连接信息
USER=$(echo $DSN | sed -E 's/.*\/\/([^:]+):.*/\1/')
PASS=$(echo $DSN | sed -E 's/.*:([^@]+)@.*/\1/')
HOST=$(echo $DSN | sed -E 's/.*@([^:]+):.*/\1/')
PORT=$(echo $DSN | sed -E 's/.*:([0-9]+)\/.*/\1/')
DB=$(echo $DSN | sed -E 's/.*\/([^\/]+)$/\1/')

MYSQL_CMD="mysql -h$HOST -P$PORT -u$USER -p$PASS $DB"

# 首先执行setup.sql创建表和数据
# $MYSQL_CMD < setup.sql

# 查询1：复杂的多表连接和聚合
$MYSQL_CMD -BNEe "EXPLAIN ANALYZE 
SELECT 
    c.country,
    p.category,
    DATE_FORMAT(o.order_date, '%Y-%m') as month,
    COUNT(DISTINCT c.customer_id) as unique_customers,
    SUM(o.quantity * p.price) as total_revenue,
    AVG(o.quantity) as avg_quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
WHERE o.order_date >= '2023-01-01'
    AND o.status = 'completed'
GROUP BY c.country, p.category, DATE_FORMAT(o.order_date, '%Y-%m')
HAVING total_revenue > 10000
ORDER BY total_revenue DESC;" > analyze.1

# 查询2：子查询和窗口函数
$MYSQL_CMD -e "EXPLAIN ANALYZE 
WITH customer_stats AS (
    SELECT 
        c.customer_id,
        c.country,
        COUNT(*) as order_count,
        SUM(o.quantity * p.price) as total_spent,
        ROW_NUMBER() OVER (PARTITION BY c.country ORDER BY SUM(o.quantity * p.price) DESC) as country_rank
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'completed'
    GROUP BY c.customer_id, c.country
)
SELECT 
    cs.*,
    c.name,
    c.email
FROM customer_stats cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE country_rank <= 5
ORDER BY country, total_spent DESC\G" > analyze.2

# 查询3：复杂条件和EXISTS子查询
$MYSQL_CMD -e "EXPLAIN ANALYZE 
SELECT 
    p.category,
    p.name as product_name,
    p.price,
    (
        SELECT COUNT(DISTINCT o.customer_id)
        FROM orders o
        WHERE o.product_id = p.product_id
        AND o.status = 'completed'
    ) as unique_buyers,
    EXISTS (
        SELECT 1
        FROM orders o2
        WHERE o2.product_id = p.product_id
        AND o2.order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    ) as has_recent_orders
FROM products p
WHERE p.stock < 100
AND p.price > (
    SELECT AVG(price) * 1.5
    FROM products
    WHERE category = p.category
)
ORDER BY p.category, unique_buyers DESC\G" > analyze.3 