"""
data_collector/yahoo_api.py
---------------
使用 yfinance 取得股票資料
"""

from utils.helpers import setup_logger
import yfinance as yf

logger = setup_logger("yahoo_api")

def fetch_stock_data(stock_code: str, start_date: str, end_date: str):
    """TODO: Add docstring for def fetch_stock_data(stock_code: str, start_date: str, end_date: str):"""
    """
    抓取股票歷史資料，回傳 list[dict]
    每筆 dict 包含：stock_id, trade_date, open_price, high_price, low_price, close_price, volume
    """
    ticker = yf.Ticker(stock_code)
    hist = ticker.history(start=start_date, end=end_date)

    if hist.empty:
        return []

    data_list = []
    for date, row in hist.iterrows():
        data_list.append({
            "stock_id": stock_code.split(".")[0],
            "trade_date": date.strftime("%Y-%m-%d"),
            "open_price": float(row["Open"]),
            "high_price": float(row["High"]),
            "low_price": float(row["Low"]),
            "close_price": float(row["Close"]),
            "volume": int(row["Volume"])
        })
    return data_list

def fetch_stock_name(stock_code: str) -> str:
    """TODO: Add docstring for def fetch_stock_name(stock_code: str) -> str:"""
    """取得股票名稱 (英文或長名稱)"""
    try:
        ticker = yf.Ticker(stock_code)
        info = ticker.info
        name = info.get("shortName") or info.get("longName") or stock_code.split(".")[0]
        return name
    except:
        return stock_code.split(".")[0]