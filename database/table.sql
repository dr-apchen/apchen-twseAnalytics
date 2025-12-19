CREATE DATABASE IF NOT EXISTS twse CHARACTER SET utf8mb4;

USE twse;

CREATE TABLE IF NOT EXISTS stock_info (
    stock_id VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(50),
    industry VARCHAR(50),
    market_type VARCHAR(20),
    listing_date DATE
);

CREATE TABLE IF NOT EXISTS stock_price_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id VARCHAR(10),
    trade_date DATE,
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    volume BIGINT,
    UNIQUE KEY uniq_stock_date (stock_id, trade_date),
    FOREIGN KEY (stock_id) REFERENCES stock_info(stock_id)
);
