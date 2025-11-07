"""
database/stock_info_manager.py
-----------
處理 stock_info 表的管理邏輯
"""

from utils.helpers import setup_logger
from database.db_connection import get_connection, close_connection

logger = setup_logger("stock_info_manager")

def ensure_stock_exists(stock_id: str, stock_name: str, industry: str = "未知", market_type: str = "TWSE", listing_date: str = None):
    """TODO: Add docstring for def ensure_stock_exists(stock_id: str, stock_name: str, industry: str = "未知", market_type: str = "TWSE", listing_date: str = None):"""
    """
    確保指定股票代號存在於 stock_info 表中
    若不存在，則自動插入一筆基本資料
    """
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    # 檢查是否已存在
    check_query = "SELECT COUNT(*) FROM stock_info WHERE stock_id = %s"
    cursor.execute(check_query, (stock_id,))
    exists = cursor.fetchone()[0] > 0

    if not exists:
        insert_query = """
            INSERT INTO stock_info (stock_id, stock_name, industry, market_type, listing_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (stock_id, stock_name, industry, market_type, listing_date))
        conn.commit()
        print(f"✅ 股票 {stock_id} ({stock_name}) 已新增至 stock_info")
    else:
        print(f"ℹ️ 股票 {stock_id} 已存在於 stock_info")

    cursor.close()
    close_connection(conn)
    return True
