# database/data_loder.py
"""
database/data_loder.py
-----------
股價資料寫入
"""

from utils.helpers import setup_logger
from database.db_connection import get_connection, close_connection
from database.stock_info_manager import ensure_stock_exists
from utils.stock_info_map import get_stock_name, get_stock_type
from data_collector.twse_crawler import fetch_twse_stock_list

logger = setup_logger("data_loder")

def insert_stock_price(data):
    """TODO: Add docstring for def insert_stock_price(data):"""
    """
    將股價資料寫入 stock_price_daily
    data 為 list[dict]，每筆 dict 需包含：
    ['stock_id', 'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
    """
    if not data:
        print("⚠️ 無資料可寫入。")
        return

    stock_id = data[0]["stock_id"]
    stock_name = get_stock_name(stock_id)
    if not stock_name:
        fetch_twse_stock_list()  # 自動抓取最新中文名稱表   
    stock_type = get_stock_type(stock_id)

    # 確保股票存在於 stock_info
    ensure_stock_exists(stock_id, stock_name=stock_name, market_type=stock_type)

    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    insert_query = """
        INSERT INTO stock_price_daily
        (stock_id, trade_date, open_price, high_price, low_price, close_price, volume)
        VALUES (%(stock_id)s, %(trade_date)s, %(open_price)s, %(high_price)s, %(low_price)s, %(close_price)s, %(volume)s)
        ON DUPLICATE KEY UPDATE
            open_price = VALUES(open_price),
            high_price = VALUES(high_price),
            low_price = VALUES(low_price),
            close_price = VALUES(close_price),
            volume = VALUES(volume);
    """
    try:
        cursor.executemany(insert_query, data)
        conn.commit()
        print(f"✅ 已成功寫入 {len(data)} 筆 {stock_id} 資料")
    except Exception as e:
        print("❌ 寫入失敗：", e)
        conn.rollback()
    finally:
        cursor.close()
        close_connection(conn)
