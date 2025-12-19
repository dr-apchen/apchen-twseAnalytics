CREATE DATABASE IF NOT EXISTS twse CHARACTER SET utf8mb4;

USE twse;

CREATE TABLE IF NOT EXISTS stock_info (
    stock_id VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(50),
    sector VARCHAR(50),
    industry VARCHAR(50) DEFAULT '未知',
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
    updated_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_stock_date (stock_id, trade_date),
    FOREIGN KEY (stock_id) REFERENCES stock_info(stock_id)
);

CREATE TABLE IF NOT EXISTS institutional_trades (
    -- 核心識別資訊
    trade_date DATE NOT NULL COMMENT '交易日期',
    stock_id VARCHAR(10) NOT NULL COMMENT '股票代碼',
    
    -- 外資買賣超 (Foreign Investor)
    foreign_buy_shares BIGINT NOT NULL COMMENT '外資買進股數',
    foreign_sell_shares BIGINT NOT NULL COMMENT '外資賣出股數',
    foreign_net_shares BIGINT GENERATED ALWAYS AS (foreign_buy_shares - foreign_sell_shares) STORED COMMENT '外資淨買入股數 (計算欄位)',
    
    -- 投信買賣超 (Investment Trust)
    trust_buy_shares BIGINT NOT NULL COMMENT '投信買進股數',
    trust_sell_shares BIGINT NOT NULL COMMENT '投信賣出股數',
    trust_net_shares BIGINT GENERATED ALWAYS AS (trust_buy_shares - trust_sell_shares) STORED COMMENT '投信淨買入股數 (計算欄位)',
    
    -- 自營商買賣超 (Dealer)
    dealer_buy_shares BIGINT NOT NULL COMMENT '自營商買進股數',
    dealer_sell_shares BIGINT NOT NULL COMMENT '自營商賣出股數',
    dealer_net_shares BIGINT GENERATED ALWAYS AS (dealer_buy_shares - dealer_sell_shares) STORED COMMENT '自營商淨買入股數 (計算欄位)',

    -- 設置複合主鍵：確保每天每支股票只有一筆紀錄
    PRIMARY KEY (trade_date, stock_id),
    
    -- 設置外鍵約束 (如果您的 stock_info 表已建立，這可以保證數據完整性)
    -- CONSTRAINT fk_stock_id FOREIGN KEY (stock_id) REFERENCES tw_stock_list(stock_id) 
    
    -- 設置引擎和編碼
    KEY idx_stock_id (stock_id) -- 額外索引，用於按股票代碼查詢歷史數據
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='三大法人每日買賣超數據';