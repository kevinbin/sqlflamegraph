-- 创建测试表
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at DATETIME,
    country VARCHAR(50)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2),
    category VARCHAR(50),
    stock INT
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT,
    order_date DATETIME,
    status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 插入测试数据
INSERT INTO customers 
SELECT 
    id,
    CONCAT('Customer ', id),
    CONCAT('customer', id, '@example.com'),
    DATE_ADD('2023-01-01 00:00:00', INTERVAL FLOOR(RAND() * 365) DAY),
    ELT(1 + FLOOR(RAND() * 3), 'USA', 'China', 'Europe')
FROM (SELECT @rownum:=@rownum+1 as id FROM (SELECT @rownum:=0) r, information_schema.columns LIMIT 1000) AS seq;

INSERT INTO products 
SELECT 
    id,
    CONCAT('Product ', id),
    50 + RAND() * 950,
    ELT(1 + FLOOR(RAND() * 4), 'Electronics', 'Clothing', 'Books', 'Food'),
    FLOOR(RAND() * 1000)
FROM (SELECT @rownum:=@rownum+1 as id FROM (SELECT @rownum:=0) r, information_schema.columns LIMIT 100) AS seq;

INSERT INTO orders 
SELECT 
    id,
    1 + FLOOR(RAND() * 1000),
    1 + FLOOR(RAND() * 100),
    1 + FLOOR(RAND() * 5),
    DATE_ADD('2023-01-01 00:00:00', INTERVAL FLOOR(RAND() * 365) DAY),
    ELT(1 + FLOOR(RAND() * 3), 'completed', 'pending', 'cancelled')
FROM (SELECT @rownum:=@rownum+1 as id FROM (SELECT @rownum:=0) r, information_schema.columns LIMIT 10000) AS seq; 