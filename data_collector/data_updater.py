"""
data_collector/data_updater.py
---------------
負責檢查資料庫資料完整性，若使用者查詢區間內有缺資料，
則自動從 Yahoo Finance 補抓並寫入 MySQL。
同時確保台股清單存在。
"""

from utils.helpers import setup_logger
from datetime import datetime, date, timedelta
from database.db_connection import get_connection, close_connection
from data_collector.yahoo_api import fetch_stock_data, fetch_stock_name
from database.data_loader import insert_stock_price
from utils.stock_info_map import get_stock_name, get_stock_type
import pandas as pd

logger = setup_logger("data_updater")

# ---------------------
# 載入資料
# ---------------------
def load_stock_data(conn, stock_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    從資料庫讀取股價資料
    
    參數：
        stock_id (str): 股票代碼
        start_date (str): 查詢起始日期
        end_date (str): 查詢結束日期
    
    返回：
        df (pd.Dataframe): 股價資料
    """
    if not conn:
        raise ValueError("需要提供資料庫連接實例。")
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

    if not rows:
        print("⚠️ 無資料可分析")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df.sort_values("trade_date")
    return df


# ---------------------
# 資料檢查(更新日期)
# ---------------------
def check_stock_data_uptodate(conn, stock_ids: list[str], start_date: str = None, end_date: str = None) -> list[str]:
    """
    確認目標股股價資料存在於資料庫
    
    參數：
        stock_id (str): 股票代碼
    
    返回：
        count > 0 (bool)
    """
    
    if not conn:
        raise ValueError("需要提供資料庫連接實例。")
        return False
    cursor = conn.cursor()
    stock_uptodate = []
    query = "SELECT stock_id FROM stock_price_daily WHERE stock_id IN ("
    for i in range(len(stock_ids)):
        print(f"🚀 確認 {stock_ids[i]} 股價資料筆數...")
        stock_id = "'" + stock_ids[i] + "'"
        query += (", " if i > 0 else "") + stock_id
    query += ") AND updated_date >= CURDATE();"
    cursor.execute(query)
    stock_uptodate = cursor.fetchall()
    cursor.close()
    return stock_uptodate
# ---------------------
# 資料檢查
# ---------------------
def check_stock_data_exists(conn, stock_id: str, start_date: str, end_date: str) -> bool:
    """
    確認目標股股價資料存在於資料庫
    
    參數：
        stock_id (str): 股票代碼
        start_date (str): 查詢起始日期
        end_date (str): 查詢結束日期
    
    返回：
        count > 0 (bool)
    """
    
    print(f"🚀 確認 {stock_id} 股價資料筆數...")
    if not conn:
        raise ValueError("需要提供資料庫連接實例。")
        return False
    cursor = conn.cursor()
    query = """
        SELECT COUNT(*) FROM stock_price_daily 
        WHERE stock_id = %s AND trade_date BETWEEN %s AND %s
    """
    cursor.execute(query, (stock_id, start_date, end_date))
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0

# ---------------------
# 動態抓資料
# ---------------------
def fetch_and_store(conn, stock_id: str, start_date: str, end_date: str) -> bool:
    """
    抓取資料並寫入資料庫，stock_name 可自動抓取
    
    參數：
        stock_id (str): 股票代碼
        start_date (str): 查詢起始日期
        end_date (str): 查詢結束日期
    
    返回：
        NA
    """
    if not conn:
        raise ValueError("需要提供資料庫連接實例。")
        return False
    stock_name = get_stock_name(stock_id)
    if stock_name != stock_id:  # 台股
        stock_type = get_stock_type(stock_id)
        stock_id = f"{stock_id}.{stock_type}"
    else:
        stock_name = fetch_stock_name(stock_id)

    print(f"🚀 開始抓取 {stock_id} 股價資料...")
    data = fetch_stock_data(stock_id, start_date=start_date, end_date=end_date)

    if data:
        insert_stock_price(conn, data)
        print(f"✅ {stock_id} ({stock_name}) 股價資料寫入完成！")
        return True
    else:
        print("⚠️ 無資料可寫入")
        return False
        
def get_stock_latest_date(cursor, stock_id):
    """
    從資料庫讀取股價資料"
    
    參數：
        cursor (conn.cursor(dictionary=True))
        stock_id (str): 股票代碼
    
    返回：
        df (pd.Dataframe): 資料庫最新交易日
    """
    print(f"🚀 確認 {stock_id} 股價資料的最後更新日期...")
    if not stock_id:
        print("⚠️ 遺失 stock ID")
        return
    else:
        print(f"🚀 開始抓取 {stock_id} 最後交易日...")
        query = """
            SELECT MAX(trade_date)
            FROM stock_price_daily
            WHERE stock_id = %s
        """
        cursor.execute(query, (stock_id,))
        result = cursor.fetchone()
        
        return result["MAX(trade_date)"] if result and result["MAX(trade_date)"] else None


def update_stock_if_needed(stock_id, stock_name, start_date=None, end_date=None, days_tolerance=1):
    """
    檢查個別股票是否最新，若缺資料則自動更新。
    
    參數：
        stock_id (str): 股票代碼
        stock_name (str): 股票名稱
        start_date (str): 查詢起始日期
        end_date (str): 查詢結束日期
        days_tolerance (int): 緩衝區間
    
    返回：
        updated (bool): 更新成功與否
    """
    print(f"🚀 檢查是否須抓取最新 {stock_id} 股價資料...")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    today = date.today()
    updated = False

    latest_date = get_stock_latest_date(cursor, stock_id)
    if not latest_date or (today - latest_date).days > days_tolerance:
        print(f"🔄 更新中: {stock_id} {stock_name} (最後資料: {latest_date})")
        start_date = latest_date + timedelta(days=1) if latest_date else today - timedelta(days=365)
        fetch_and_store(stock_id, start_date, end_date or today)
        updated = True
    else:
        print(f"✅ {stock_id} {stock_name} 資料已是最新 ({latest_date})")

    cursor.close()
    conn.close()
    return updated


def update_all_stocks(days_tolerance=1):
    """
    檢查所有股票資料是否為最新，如缺少最近資料則自動補抓。
    
    參數：
        days_tolerance (int): 緩衝區間
    
    返回：
        NA
    """
    
    print(f"🚀 檢查是否須抓取最新所有股價資料...")
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

        if not latest_date or (today - latest_date).days > days_tolerance:
            print(f"🔄 更新中: {stock_id} {stock_name} (最後資料: {latest_date})")
            start_date = latest_date + timedelta(days=1) if latest_date else today - timedelta(days=365)
            fetch_and_store(stock_id, start_date, today)
            updated_count += 1
        else:
            print(f"✅ {stock_id} {stock_name} 資料已是最新 ({latest_date})")

    cursor.close()
    conn.close()
    print(f"\n📊 全部更新完成，共更新 {updated_count} 檔股票。")


def load_foreign_net_buy(conn, stock_ids: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    載入特定股票在指定區間的外資淨買賣超數據。

    Args:
        stock_ids (list[str]): 股票代碼。
        start_date (str): 查詢起始日期 (YYYY-MM-DD)。
        end_date (str): 查詢結束日期 (YYYY-MM-DD)。
        db_conn (DBConnection): 資料庫連接實例。

    Returns:
        pd.DataFrame: 包含 trade_date, foreign_net_shares 的數據。
    """
    if not conn:
        raise ValueError("需要提供資料庫連接實例。")
        return False
    cursor = conn.cursor(dictionary=True)
    
    # 建立 stock_id 佔位符列表 (e.g., ['%s', '%s', '%s'])
    stock_id_placeholders = ', '.join(['%s'] * len(stock_ids))
    # 組合參數：stock_ids 的參數 (元組) 加上日期的參數
    params = tuple(stock_ids) + (start_date, end_date)
    
    # SQL 查詢語句
    query = f"""
    SELECT 
        trade_date,
        stock_id,
        foreign_net_shares
    FROM 
        institutional_trades
    WHERE 
        stock_id IN ({stock_id_placeholders}) AND 
        trade_date BETWEEN %s AND %s
    ORDER BY 
        trade_date ASC, stock_id ASC;
    """
    # try:
    cursor.execute(query, params)
    result = cursor.fetchall()
    df = pd.DataFrame(result)
    cursor.close()
    
    if df.empty:
        print(f"找不到 {stock_ids} 在 {start_date} 至 {end_date} 的外資交易數據。")
        return pd.DataFrame(columns=['trade_date', 'foreign_net_shares'])
        
    # 確保日期是 datetime 格式，並設為索引（有利於時間序列分析）
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    
    return df
        
    # except Exception as e:
    #     print(f"載入外資淨買賣數據時發生錯誤 ({stock_ids}): {e}")
    #     return pd.DataFrame(columns=['trade_date', 'foreign_net_shares'])

def load_daily_all_institutional_data(conn, target_date: str, n: int = 50) -> pd.DataFrame:
    """
    載入特定日期所有股票的外資淨買賣數據，並嘗試加入產業資訊。
    
    Args:
        target_date (str): 查詢日期 (YYYY-MM-DD)。
        db_conn: 資料庫連接實例。
        
    Returns:
        pd.DataFrame: 包含 stock_id, foreign_net_shares, industry 等欄位。
    """
    if not conn:
        raise ValueError("需要提供資料庫連接實例。")
        return False
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        it.trade_date,
        it.stock_id, 
        it.foreign_net_shares,
        si.industry
    FROM 
        institutional_trades it
    LEFT JOIN 
        stock_info si ON it.stock_id = si.stock_id
    WHERE 
        it.trade_date = %s
    ORDER BY 
        it.foreign_net_shares DESC
    LIMIT %s;
    """
    params = (target_date,n)
    
    # try:
    cursor.execute(query, params)
    result = cursor.fetchall()
    df = pd.DataFrame(result)
    cursor.close()
    
    if df.empty:
        print(f"找不到在 {target_date} 的外資交易數據。")
        return pd.DataFrame(columns=['trade_date', 'foreign_net_shares'])
        
    # 確保日期是 datetime 格式，並設為索引（有利於時間序列分析）
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    
    return df
    
    # except Exception as e:
    #     print(f"載入外資淨買賣數據時發生錯誤 ({target_date}): {e}")
    #     return pd.DataFrame(columns=['trade_date', 'foreign_net_shares'])