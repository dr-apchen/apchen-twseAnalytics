"""
data_collector/twse_crawler.py
---------------
爬取台股上市/上櫃股票基本資訊並匯出成CSV檔
"""

from utils.helpers import setup_logger
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib3

logger = setup_logger("twse_crawler")

TWSE_URL = {"TW": "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", "TWO": "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"}

def fetch_twse_stock_list(save_path="data/tw_stock_list.csv"):
    """TODO: Add docstring for def fetch_twse_stock_list(save_path="data/tw_stock_list.csv"):"""
    """爬取台股上市/上櫃股票代碼與中文名稱，並更新 CSV"""
    
    stock_list = []
    for key in TWSE_URL:
        response = twse_request(TWSE_URL[key])
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", class_= 'h4')
        if not tables:
            print("❌ 找不到表格資料")
            return
        for row in tables[0].find_all("tr")[2:]:
            cols = row.find_all("td")
            if len(cols) >= 5:
                stock = cols[0].text.split('　')
                if stock[0].isdigit():
                    stock_list.append({"stock_id": stock[0], "stock_name": stock[1], "stock_type": key})

    df = pd.DataFrame(stock_list)
    df.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"✅ 已更新台股中文名稱對照表，共 {len(df)} 檔股票")

def twse_request(url: str):
    """TODO: Add docstring for def twse_request(url: str):"""
    try:
        # 使用 certifi 提供的憑證進行 SSL 驗證
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, verify=False)
        response.encoding = "big5"
        return response
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL 驗證失敗: {e}")
        return
    