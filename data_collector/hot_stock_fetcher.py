"""
data_collector/hot_stock_fetcher.py

功能：
    - 取得台股熱門股票清單（包含 TWSE 上市 與 TPEx 上櫃）
    - 若網路或解析失敗，會自動載入本地快取 data/hot_stocks.csv
    - 支援儲存快取檔案與回傳 DataFrame

回傳欄位：
    - StockID   : 股票代碼 (e.g. 2330)
    - StockName : 中文名稱 (若可取得)
    - Volumn    : 股票成交量 (股數)
    - Market    : TWSE 或 TPEx
    - UpdateTime: 快取建立時間（字串）
"""

from utils.helpers import setup_logger
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib3
import requests
import time
import pandas as pd
import re

logger = setup_logger("hot_stock_fetcher")

# ========== 設定 ==========
TWSE_API_URL = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALLBUT0999"
TPEx_RANK_URL = "https://www.tpex.org.tw/zh-tw/mainboard/trading/historical/rank-volume/day.html"
CACHE_PATH = os.path.join("data", "hot_stocks.csv")


def fetch_hot_stocks_twse(limit: int = 20) -> pd.DataFrame:
    """
    從 TWSE 取得熱門股票（以成交量或熱門排行為依據）。

    Args:
        limit (int): 取前 N 筆（預設 20）。

    Returns:
        pd.DataFrame: 欄位包含 StockID, StockName, Market
    """
    JSON_KEYWORD = "每日收盤行情"

    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = requests.get(TWSE_API_URL, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        # response = twse_request(TWSE_API_URL)
        # data = response.json()
        # TWSE 回傳多個 dataX 與 fieldsX, 嘗試找到含「證券代號」或 "StockID" 的表格欄位
        df = None 
        for items in data["tables"]:
            title = re.search(JSON_KEYWORD, items["title"])
            if title is not None:
                df = pd.DataFrame()
                # df.columns=["StockID", "StockName", "Volumn", "Market"]
                df["StockID"] = pd.DataFrame(((items["data"][i][0]).strip() for i in range(len(items["data"]))))
                df["StockName"] = pd.DataFrame(((items["data"][i][1]).strip() for i in range(len(items["data"]))))
                df["Volumn"] = pd.DataFrame((int((items["data"][i][2]).strip().replace(",", "")) for i in range(len(items["data"]))))
                df["Market"] = pd.DataFrame(("TW" for i in range(len(items["data"]))))
                df_limit = df.sort_values(by='Volumn', ascending=False).copy().head(limit)
                print(f"✅ TWSE抓取完成，共 {len(df)} 筆 (限制 {limit})")
                return df_limit

        if df is None:
            raise ValueError("TWSE 回傳格式非預期，無法解析")

    except Exception as e:
        # 不要 raise（以免中斷整個流程），改回傳空 DataFrame
        print(f"⚠️ fetch_hot_stocks_twse 失敗：{e}")
        return pd.DataFrame(columns=["StockID", "StockName", "Volumn", "Market"])


def fetch_hot_stocks_tpex(limit: int = 20) -> pd.DataFrame:
    """
    從 TPEx (櫃買中心) 取得熱門股票排行（以成交量排行頁面抓取為主）。

    Args:
        limit (int): 取前 N 筆（預設 20）。

    Returns:
        pd.DataFrame: 欄位包含 StockID, StockName, Market
    """
    try:
        
        options = webdriver.ChromeOptions()        
        options.add_argument('--headless')  # 設定動態爬蟲在背景執行
        driver = webdriver.Chrome(options=options)
        # driver = webdriver.Chrome()
        driver.implicitly_wait(5)
        driver.get(TPEx_RANK_URL)
        time.sleep(2)
        df = None 
        df1, df2, df3, df4 = [], [], [], []
        while True:
            nextBtn = driver.find_element(By.CSS_SELECTOR, "a.page-link.next")
            soup = BeautifulSoup(driver.page_source, "lxml")
            soup.prettify()
            rows = soup.select("div.main-content > div > table > tbody > tr")
            if rows is not None:
                df1.extend([rows[i].find_all("td")[1].text.strip() for i in range(len(rows))])
                df2.extend([rows[i].find_all("td")[2].text.strip() for i in range(len(rows))])
                df3.extend([int(rows[i].find_all("td")[3].text.strip().replace(",", "")) for i in range(len(rows))])
                df4.extend(["TWO" for i in range(len(rows))])
                
                if len(df1) < limit and nextBtn is not None:
                    nextBtn.click()
                    continue
                else: 
                    df = pd.concat([pd.DataFrame(df1), pd.DataFrame(df2), pd.DataFrame(df3), pd.DataFrame(df4)], axis=1)
                    df.columns=["StockID", "StockName", "Volumn", "Market"]
                    df_limit = df.sort_values(by='Volumn', ascending=False).copy().head(limit)
                    print(f"✅ TPEX抓取完成，共 {len(df)} 筆 (限制 {limit})")
                    driver.quit() 
                    return df_limit

        if df is None:
            raise ValueError("TPEX 回傳格式非預期，無法解析")
    
    except Exception as e:
        print(f"⚠️ fetch_hot_stocks_tpex 失敗：{e}")
        return pd.DataFrame(columns=["StockID", "StockName", "Volumn", "Market"])

def merge_and_save_hot_stocks(limit: int = 20) -> pd.DataFrame:
    """
    合併 TWSE 與 TPEx 的熱門股票，去重並儲存為本地快取。

    Args:
        limit (int): 每個市場的取樣數量（預設 20）。

    Returns:
        pd.DataFrame: 合併並儲存的熱門股票清單。
    """
    twse_df = fetch_hot_stocks_twse(limit=limit*2)
    tpex_df = fetch_hot_stocks_tpex(limit=limit*2)

    combined = pd.concat([twse_df, tpex_df], ignore_index=True, sort=False)
    # 保留 StockID 與 StockName（若同代號以第一筆為主）
    combined = combined.drop_duplicates(subset=["StockID"], keep="first").reset_index(drop=True)

    # 補上 UpdateTime 欄位
    combined["UpdateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    combined = combined.sort_values(by='Volumn', ascending=False)
    
    # 儲存快取
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    try:
        combined.to_csv(CACHE_PATH, index=False, encoding="utf-8-sig")
    except Exception as e:
        print(f"⚠️ 寫入 hot_stocks 快取失敗：{e}")

    print(f"✅ merge_and_save_hot_stocks 完成，共 {len(combined)} 筆 (限制 {limit})")
    return combined


def load_hot_stocks_from_cache() -> pd.DataFrame:
    """
    載入本地快取的熱門股票清單（若不存在則回傳空 DataFrame）。

    Returns:
        pd.DataFrame: 快取內容或空表格。
    """
    if os.path.exists(CACHE_PATH):
        try:
            df = pd.read_csv(CACHE_PATH, dtype=str)
            # 若檔案存在但欄位不完整，嘗試補欄位
            for col in ["StockID", "StockName", "Valumn", "Market", "UpdateTime"]:
                if col not in df.columns:
                    df[col] = ""
            return df[["StockID", "StockName", "Valumn", "Market", "UpdateTime"]]
        except Exception as e:
            print(f"⚠️ 載入 hot_stocks 快取失敗：{e}")
            return pd.DataFrame(columns=["StockID", "StockName", "Valumn", "Market", "UpdateTime"])
    else:
        return pd.DataFrame(columns=["StockID", "StockName", "Valumn", "Market", "UpdateTime"])


# ========== 便利測試區（本檔直接執行時） ==========
if __name__ == "__main__":
    # 測試抓取並顯示
    df = merge_and_save_hot_stocks(limit=30)
    print(df.head(15).to_string(index=False))
    
    # fetch_hot_stocks_twse()
    # fetch_hot_stocks_tpex()
