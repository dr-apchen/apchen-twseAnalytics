"""
database/db_config.py
-----------
MySQL 資料庫連線設定
"""

DB_CONFIG = {
    "host": "localhost",          # 或雲端資料庫 IP
    "port": 3306,
    "user": "root",               # 你的 MySQL 帳號
    "password": "root",  # 你的 MySQL 密碼
    "database": "twse",  # 資料庫名稱
    "charset": "utf8mb4"
}
