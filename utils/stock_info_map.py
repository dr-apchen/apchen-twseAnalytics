"""
utils/stock_name_map.py
-----------
取得台灣證交所上市股票代碼與中文名稱、上市櫃類別碼對照
"""

from utils.helpers import setup_logger
import pandas as pd

logger = setup_logger("stock_name_map")

try:
    stock_map = pd.read_csv("data/tw_stock_list.csv", dtype=str)
except FileNotFoundError:
    stock_map = pd.DataFrame(columns=["stock_id", "stock_name", "stock_type"])

stock_dict_n = dict(zip(stock_map.stock_id, stock_map.stock_name))
stock_dict_t = dict(zip(stock_map.stock_id, stock_map.stock_type))

def get_stock_name(stock_id: str) -> str:
    """
    取得中文名稱，找不到就回傳股票代碼
    
    參數：
        stock_data_dict (dict): 股價資訊
    
    返回型別：
        str
    """
    return stock_dict_n.get(stock_id, stock_id)

def get_stock_type(stock_id: str) -> str:
    """
    取得上市上櫃類別碼，找不到就回傳股票代碼
    
    參數：
        stock_data_dict (dict): 股價資訊
    
    返回型別：
        str
    """
    return stock_dict_t.get(stock_id, stock_id)
