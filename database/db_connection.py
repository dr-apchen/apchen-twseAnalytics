"""
database/db_connection.py
-----------
建立 MySQL 連線物件
"""

from utils.helpers import setup_logger
import mysql.connector
from mysql.connector import Error
from database.db_config import DB_CONFIG

logger = setup_logger("db_connection")

def get_connection():
    """TODO: get_connection():"""
    """建立資料庫連線"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ MySQL 連線成功")
            return connection
    except Error as e:
        print("❌ MySQL 連線失敗：", e)
        return None

def close_connection(connection):
    """TODO: Add docstring for def close_connection(connection):"""
    """關閉資料庫連線"""
    if connection and connection.is_connected():
        connection.close()
        print("🔌 資料庫連線已關閉")
