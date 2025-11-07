"""
data_collector/data_updater.py
---------------
負責檢查資料庫資料完整性，若使用者查詢區間內有缺資料，
則自動從 Yahoo Finance 補抓並寫入 MySQL。
同時確保台股清單存在。
"""

from utils.helpers import setup_logger
from datetime import date, timedelta
from database.db_connection import get_connection, close_connection
from data_collector.yahoo_api import fetch_stock_data, fetch_stock_name
from database.data_loader import insert_stock_price
from utils.stock_info_map import get_stock_name, get_stock_type
import pandas as pd

logger = setup_logger("data_updater")

# ---------------------
# 載入資料
# ---------------------
def load_stock_data(stock_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """TODO: Add docstring for def load_stock_data(stock_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:"""
    """從資料庫讀取股價資料"""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    cursor = conn.cursor(dictionary=True)

    query = f"SELECT * FROM stock_price_daily WHERE stock_id = %s"
    params = [stock_id]
    if start_date and end_date:
        query += " AND trade_date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    close_connection(conn)

    if not rows:
        print("⚠️ 無資料可分析")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df.sort_values("trade_date")
    return df


# ---------------------
# 資料檢查
# ---------------------
def check_stock_data_exists(stock_id: str, start_date: str, end_date: str) -> bool:
    """TODO: Add docstring for def check_stock_data_exists(stock_id: str, start_date: str, end_date: str) -> bool:"""
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    query = """
        SELECT COUNT(*) FROM stock_price_daily 
        WHERE stock_id = %s AND trade_date BETWEEN %s AND %s
    """
    cursor.execute(query, (stock_id, start_date, end_date))
    count = cursor.fetchone()[0]
    cursor.close()
    close_connection(conn)
    return count > 0

# ---------------------
# 動態抓資料
# ---------------------
def fetch_and_store(stock_id: str, start_date: str, end_date: str):
    """TODO: Add docstring for def fetch_and_store(stock_id: str, start_date: str, end_date: str):"""
    """抓取資料並寫入資料庫，stock_name 可自動抓取"""
    
    if stock_id.isdigit() and len(stock_id) == 4:  # 台股
        stock_name = get_stock_name(stock_id)
        stock_type = get_stock_type(stock_id)
        stock_id = f"{stock_id}.{stock_type}"
    else:
        stock_name = fetch_stock_name(stock_id)

    print(f"🚀 開始抓取 {stock_id}.{stock_type} 股價資料...")
    data = fetch_stock_data(stock_id, start_date=start_date, end_date=end_date)

    if data:
        insert_stock_price(data)
        print(f"✅ {stock_id} ({stock_name}) 股價資料寫入完成！")
    else:
        print("⚠️ 無資料可寫入")
        
def get_stock_latest_date(cursor, stock_id):
    """TODO: Add docstring for def get_stock_latest_date(cursor, stock_id):"""
    query = """
        SELECT MAX(trade_date)
        FROM stock_price_daily
        WHERE stock_id = %s
    """
    cursor.execute(query, (stock_id,))
    result = cursor.fetchone()
    return result[0] if result and result[0] else None


def update_stock_if_needed(stock_id, stock_name, start_date=None, end_date=None, days_tolerance=1):
    """TODO: Add docstring for def update_stock_if_needed(stock_id, stock_name, start_date=None, end_date=None, days_tolerance=1):"""
    """
    檢查個別股票是否最新，若缺資料則自動更新。
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    today = date.today()
    updated = False

    latest_date = get_stock_latest_date(cursor, stock_id)
    if not latest_date or (today - latest_date.date()).days > days_tolerance:
        print(f"🔄 更新中: {stock_id} {stock_name} (最後資料: {latest_date})")
        start_date = latest_date + timedelta(days=1) if latest_date else today - timedelta(days=365)
        fetch_and_store(stock_id, start_date, end_date or today, stock_name)
        updated = True
    else:
        print(f"✅ {stock_id} {stock_name} 資料已是最新 ({latest_date})")

    cursor.close()
    conn.close()
    return updated


def update_all_stocks(days_tolerance=1):
    """TODO: Add docstring for def update_all_stocks(days_tolerance=1):"""
    """
    檢查所有股票資料是否為最新，如缺少最近資料則自動補抓。
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT stock_id, stock_name FROM stock_info")
    stocks = cursor.fetchall()
    today = date.today()
    updated_count = 0

    for stock in stocks:
        stock_id = stock["stock_id"]
        stock_name = stock["stock_name"]
        latest_date = get_stock_latest_date(cursor, stock_id)

        if not latest_date or (today - latest_date.date()).days > days_tolerance:
            print(f"🔄 更新中: {stock_id} {stock_name} (最後資料: {latest_date})")
            start_date = latest_date + timedelta(days=1) if latest_date else today - timedelta(days=365)
            fetch_and_store(stock_id, start_date, today, stock_name)
            updated_count += 1
        else:
            print(f"✅ {stock_id} {stock_name} 資料已是最新 ({latest_date})")

    cursor.close()
    conn.close()
    print(f"\n📊 全部更新完成，共更新 {updated_count} 檔股票。")
