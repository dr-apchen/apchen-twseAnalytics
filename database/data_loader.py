# database/data_loder.py
"""
database/data_loder.py
-----------
股價資料寫入
"""

from utils.helpers import setup_logger
from database.db_connection import get_connection, close_connection
from database.stock_info_manager import ensure_stock_exists
from utils.stock_info_map import get_stock_name, get_stock_type, get_stock_industry
from data_collector.twse_crawler import fetch_twse_stock_list
import pandas as pd

logger = setup_logger("data_loder")

def insert_stock_price(data):
    """
    將股價資料寫入 stock_price_daily
    每筆 dict 需包含：
    ['stock_id', 'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
    
    參數：
        data (dict): 股價資訊
    
    返回：
        df_summary (pd.Dataframe): 股價摘要
    """
    if not data:
        print("⚠️ 無資料可寫入。")
        return

    stock_id = data[0]["stock_id"]
    stock_name = get_stock_name(stock_id)
    if not stock_name:
        fetch_twse_stock_list()  # 自動抓取最新中文名稱表   
    stock_type = get_stock_type(stock_id)
    stock_industry = get_stock_industry(stock_id)

    # 確保股票存在於 stock_info
    ensure_stock_exists(stock_id, stock_name=stock_name, stock_industry=stock_industry, market_type=stock_type)

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

def save_institutional_data(data_df: pd.DataFrame):
    """
    將三大法人交易數據 DataFrame 寫入 institutional_trades 資料表。

    Args:
        data_df (pd.DataFrame): 包含法人交易數據的 DataFrame (來自 fetcher)。
        db_conn (DBConnection): 資料庫連接實例。
    """
    if data_df.empty:
        print("❌ 要寫入的法人數據為空，跳過寫入。")
        return
    print(data_df)
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    # 1. 定義 SQL 語句 (使用 INSERT IGNORE 或 ON DUPLICATE KEY UPDATE)
    
    # 由於我們使用了 (trade_date, stock_id) 作為 PRIMARY KEY，
    # 建議使用 ON DUPLICATE KEY UPDATE 來處理重跑或數據修正的情況。
    # 如果數據已經存在，則更新其買賣股數欄位。
    
    sql = """
    INSERT INTO institutional_trades (
        trade_date, stock_id, 
        foreign_buy_shares, foreign_sell_shares, 
        trust_buy_shares, trust_sell_shares, 
        dealer_buy_shares, dealer_sell_shares
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        foreign_buy_shares = VALUES(foreign_buy_shares),
        foreign_sell_shares = VALUES(foreign_sell_shares),
        trust_buy_shares = VALUES(trust_buy_shares),
        trust_sell_shares = VALUES(trust_sell_shares),
        dealer_buy_shares = VALUES(dealer_buy_shares),
        dealer_sell_shares = VALUES(dealer_sell_shares)
    """

    # 2. 準備要插入的數據元組列表
    # 確保 data_df 的欄位順序與 SQL 語句中的欄位順序完全一致
    data_tuple = data_df[[
        'trade_date', 'stock_id', 
        'foreign_buy_shares', 'foreign_sell_shares', 
        'trust_buy_shares', 'trust_sell_shares', 
        'dealer_buy_shares', 'dealer_sell_shares'
    ]].values.tolist()

    try:
        # 3. 執行批量插入 (這是提高效率的關鍵)
        # 假設 db_conn 提供了 execute_many 或類似的批量操作接口
        cursor.executemany(sql, data_tuple)
        conn.commit()
        print(f"✅ 成功將 {len(data_tuple)} 筆法人交易數據寫入資料庫。")
        
    except Exception as e:
        print(f"❌ 寫入法人交易數據時發生錯誤: {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        close_connection(conn)
