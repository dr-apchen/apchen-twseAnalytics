"""
utils/stock_name_map.py
-----------
取得台灣證交所上市股票代碼與中文名稱、上市櫃類別碼對照
"""
import os.path
from utils.helpers import setup_logger
import pandas as pd
from data_collector.twse_crawler import fetch_twse_stock_list

logger = setup_logger("stock_name_map")

file_name = "data/tw_stock_list.csv"

if os.path.isfile(file_name):
    print(f"✅ 確認台股中文名稱對照表 '{file_name}' 檔案存在")
else:
    print(f"🚀 開始抓取台股中文名稱產業對照表...")
    fetch_twse_stock_list()
    
try:
    stock_map = pd.read_csv("data/tw_stock_list.csv", dtype=str)
except FileNotFoundError:
    stock_map = pd.DataFrame(columns=["stock_id", "stock_name", "stock_industry", "stock_type"])

stock_dict_n = dict(zip(stock_map.stock_id, stock_map.stock_name))
stock_dict_t = dict(zip(stock_map.stock_id, stock_map.stock_type))
stock_dict_i = dict(zip(stock_map.stock_id, stock_map.stock_industry))
industry_set = set(i for i in list(zip(stock_map.stock_industry)))
    
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
    取得上市上櫃類別碼，找不到就回傳未知
    
    參數：
        stock_data_dict (dict): 股價資訊
    
    返回型別：
        str
    """
    return stock_dict_t.get(stock_id, "未知")

def get_stock_industry(stock_id: str) -> str:
    """
    取得上市上櫃產業別，找不到就回傳未知
    
    參數：
        stock_data_dict (dict): 股價資訊
    
    返回型別：
        str
    """
    return stock_dict_i.get(stock_id, "未知")


def get_all_industry() -> list[str]:
    """
    取得上市上櫃所有產業別名稱
    
    參數：
        NA
    
    返回型別：
        list[str]
    """
    stock_industry = list(stock_map.stock_industry)
    return list(dict.fromkeys([str(i) for i in stock_industry]))
    
def get_stock_ids_by_industry(industry: str) -> list[str]:
    """
    根據產業別取得上市上櫃股票代碼
    
    參數：
        industry (str): 產業別
    
    返回型別：
        list[str]
    """
    industry_stock_ids = [str(key) for key, value in stock_dict_i.items() if value == industry]
    return industry_stock_ids