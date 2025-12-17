"""
data_collector/institutional_investor_fetcher.py
----------------
功能：
    - 取得台股三大法人買賣清單（包含 TWSE 上市 與 TPEx 上櫃）
    - 若網路或解析失敗，會自動載入本地快取 data/institutional_investor.csv
    - 支援儲存快取檔案與回傳 DataFrame

回傳欄位：
    - 'trade_date': 交易日期
    - 'stock_id': 股票代碼
    - 'foreign_buy_shares': 外資買進股數
    - 'foreign_sell_shares': 外資賣出股數
    - 'trust_buy_shares': 投信買進股數
    - 'trust_sell_shares': 投信賣出股數
    - 'dealer_buy_shares': 自營商買進股數
    - 'dealer_sell_shares': 自營商賣出股數
    
"""
from utils.helpers import setup_logger
import os
import requests
import pandas as pd
from datetime import date
from datetime import datetime
import urllib3
from database.data_loader import save_institutional_data

logger = setup_logger("institutional_investor_fetcher")

class InstitutionalFetcher:
    
    TWSE_URL = "https://www.twse.com.tw/fund/T86?response=json&selectType=ALLBUT0999" #&date={date}
    TPEX_URL = "https://www.tpex.org.tw/openapi/v1/tpex_3insti_daily_trading" # TPEx API 不需日期參數，通常返回最新資料

    def fetch_data_twse(self, target_date: datetime.date = date.today()) -> pd.DataFrame:
        """
        抓取臺灣證券交易所 (集中市場) 的三大法人數據。
        """
        date_str = target_date.strftime("%Y%m%d")
        # url = self.TWSE_URL.format(date=date_str)
        
        print(f"🚀 開始抓取 TWSE {self.TWSE_URL} 三大法人數據...")
        # try:
        # response = requests.get(url, timeout=15)
        # response.raise_for_status()
        # data = response.json()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = requests.get(self.TWSE_URL, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        # --- 檢查 TWSE 響應 ---
        if data.get('stat') != 'OK':
            print(f"❌ TWSE 抓取失敗: {data.get('stat')}")
            return pd.DataFrame()
        
        
        # 獲取主要數據區塊
        columns = [
            "證券代號",
            "證券名稱",
            "外陸資買進股數(不含外資自營商)",
            "外陸資賣出股數(不含外資自營商)",
            "外陸資買賣超股數(不含外資自營商)",
            "外資自營商買進股數",
            "外資自營商賣出股數",
            "外資自營商買賣超股數",
            "投信買進股數",
            "投信賣出股數",
            "投信買賣超股數",
            "自營商買賣超股數",
            "自營商買進股數(自行買賣)",
            "自營商賣出股數(自行買賣)",
            "自營商買賣超股數(自行買賣)",
            "自營商買進股數(避險)",
            "自營商賣出股數(避險)",
            "自營商買賣超股數(避險)",
            "三大法人買賣超股數"
        ] # K 表示千股 (張)
        
        df = pd.DataFrame(data['data'], columns=columns)
        df.replace(to_replace=r',', value=r'', regex=True, inplace=True)
        df.fillna(0, inplace=True)
        trade_date = data.get("date")
        datetime_object = datetime.strptime(trade_date, '%Y%m%d')
        df['trade_date'] = datetime_object.strftime('%Y-%m-%d')
        df['外資買進股數'] = df['外陸資買進股數(不含外資自營商)'].astype(int) + df['外資自營商買進股數'].astype(int)
        df['外資賣出股數'] = df['外陸資賣出股數(不含外資自營商)'].astype(int) + df['外資自營商賣出股數'].astype(int)
        df['外資買賣超股數'] = df['外陸資買賣超股數(不含外資自營商)'].astype(int) + df['外資自營商買賣超股數'].astype(int)
        df['自營商買進股數'] = df['自營商買進股數(自行買賣)'].astype(int) + df['自營商買進股數(避險)'].astype(int)
        df['自營商賣出股數'] = df['自營商賣出股數(自行買賣)'].astype(int) + df['自營商賣出股數(避險)'].astype(int)
        
        df.drop(columns=[
            "外陸資買進股數(不含外資自營商)",
            "外陸資賣出股數(不含外資自營商)",
            "外陸資買賣超股數(不含外資自營商)",
            "外資自營商買進股數",
            "外資自營商賣出股數",
            "外資自營商買賣超股數",
            "自營商買進股數(自行買賣)",
            "自營商賣出股數(自行買賣)",
            "自營商買賣超股數(自行買賣)",
            "自營商買進股數(避險)",
            "自營商賣出股數(避險)",
            "自營商買賣超股數(避險)"
        ], inplace=True)
        
        
        # 統一欄位名稱
        df.rename(columns={
            '證券代號': 'stock_id',
            '證券名稱': 'stock_name',
            '外資買進股數': 'foreign_buy_shares',
            '外資賣出股數': 'foreign_sell_shares',
            '外資買賣超股數': 'foreign_net_shares',
            '投信買進股數': 'trust_buy_shares',
            '投信賣出股數': 'trust_sell_shares',
            '投信買賣超股數': 'trust_net_shares',
            '自營商買進股數': 'dealer_buy_shares',
            '自營商賣出股數': 'dealer_sell_shares',
            '自營商買賣超股數': 'dealer_net_shares',
            '三大法人買賣超股數': 'institutional_net_shares'
        }, inplace=True)
        
        print(f"✅ 成功抓取 {df['trade_date'].iloc[0]} {len(df)} 筆 TWSE 法人交易數據。")
        return df
        
        # except Exception as e:
        #     print(f"❌ TWSE 數據抓取錯誤於 {date_str}: {e}")
        #     return pd.DataFrame()

    def fetch_data_tpex(self, target_date: datetime.date = date.today()) -> pd.DataFrame:
        """
        抓取櫃買中心 (上櫃市場) 的三大法人數據。
        """
        
        date_str = target_date.strftime("%Y%m%d")
        
        print(f"🚀 開始抓取 TPEx {self.TPEX_URL} 三大法人數據...")
        # try:
        # response = requests.get(self.TPEX_URL, timeout=15)
        # response.raise_for_status()
        # data = response.json()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = requests.get(self.TPEX_URL, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        
        # --- 檢查 TPEx 響應 ---
        if not isinstance(data, list) or not data:
            print("❌ TPEx 抓取失敗或無數據。")
            return pd.DataFrame()

        columns = [
           "Date",
           "SecuritiesCompanyCode",
           "CompanyName",
           "Foreign Investors include Mainland Area Investors (Foreign Dealers excluded)-Total Buy",
           " Foreign Investors include Mainland Area Investors (Foreign Dealers excluded)-Total Sell",
           "Foreign Investors include Mainland Area Investors (Foreign Dealers excluded)-Difference",
           "Foreign Dealers-Total Buy",
           "Foreign Dealers-TotalSell",
           "ForeignDealers-Difference",
           "ForeignInvestorsIncludeMainlandAreaInvestors-TotalBuy",
           "ForeignInvestorsIncludeMainlandAreaInvestors-TotalSell",
           "ForeignInvestorsInclude MainlandAreaInvestors-Difference",
           "SecuritiesInvestmentTrustCompanies-TotalBuy",
           "SecuritiesInvestmentTrustCompanies-TotalSell",
           "SecuritiesInvestmentTrustCompanies-Difference",
           "Dealers-TotalBuy",
           "Dealers-TotalSell",
           "Dealers-Difference",
           "Dealers -TotalSell",
           "TotalDifference"
        ] # K 表示千股 (張)
        
        df = pd.DataFrame(data, columns=columns)
        df.replace(to_replace=r',', value=r'', regex=True, inplace=True)
        df.fillna(0, inplace=True)
        
        trade_date = df["Date"].astype(int)
        trade_date = str(trade_date.iloc[0] + 19110000)
        datetime_object = datetime.strptime(trade_date, '%Y%m%d')
        df['trade_date'] = datetime_object.strftime('%Y-%m-%d')
        
        df.drop(columns=[
           "Date",
           "Foreign Investors include Mainland Area Investors (Foreign Dealers excluded)-Total Buy",
           " Foreign Investors include Mainland Area Investors (Foreign Dealers excluded)-Total Sell",
           "Foreign Investors include Mainland Area Investors (Foreign Dealers excluded)-Difference",
           "Foreign Dealers-Total Buy",
           "Foreign Dealers-TotalSell",
           "ForeignDealers-Difference",
           "Dealers -TotalSell"
        ], inplace=True)
        
        # 統一欄位名稱
        df.rename(columns={
            'SecuritiesCompanyCode': 'stock_id',
            'CompanyName': 'stock_name',
            'ForeignInvestorsIncludeMainlandAreaInvestors-TotalBuy': 'foreign_buy_shares',
            'ForeignInvestorsIncludeMainlandAreaInvestors-TotalSell': 'foreign_sell_shares',
            'ForeignInvestorsInclude MainlandAreaInvestors-Difference': 'foreign_net_shares',
            'SecuritiesInvestmentTrustCompanies-TotalBuy': 'trust_buy_shares',
            'SecuritiesInvestmentTrustCompanies-TotalSell': 'trust_sell_shares',
            'SecuritiesInvestmentTrustCompanies-Difference': 'trust_net_shares',
            'Dealers-TotalBuy': 'dealer_buy_shares',
            'Dealers-TotalSell': 'dealer_sell_shares',
            'Dealers-Difference': 'dealer_net_shares',
            'TotalDifference': 'institutional_net_shares'
        }, inplace=True)
        
        print(f"✅ 成功抓取 {df['trade_date'].iloc[0]} {len(df)} 筆 TPEx 法人交易數據。")
        return df

        # except Exception as e:
        #     print(f"❌ TPEx 數據抓取錯誤於 {date_str}: {e}")
        #     return pd.DataFrame()

    def combine_and_transform(self, twse_df: pd.DataFrame, tpex_df: pd.DataFrame) -> pd.DataFrame:
        """
        合併 TWSE 和 TPEx 數據，進行單位轉換，並統一欄位名稱。
        """
        CACHE_PATH = os.path.join("data", "institutional_investor.csv")
        
        if twse_df.empty and tpex_df.empty:
            return pd.DataFrame()

        # 1. 統一合併所有數據
        combined_df = pd.concat([twse_df, tpex_df], ignore_index=True)

        # 2. 欄位選擇和重命名 (從 API 欄位到 DB 欄位)
        # 假設您的 API 數據已經過清洗，只留下 'stock_id', 'trade_date' 和 各項 'XXX_shares_K'
        
        # 建立一個映射字典，將 K 股轉換為實際股數 (乘以 1000)
        # 注意：這裡需要根據您實際抓取到的欄位名稱進行精確匹配！
        final_df = combined_df
        
        # 3. 單位轉換：張數 (K) 轉換為股數 (張數 * 1000)
        share_cols = [col for col in final_df.columns if 'shares' in col]
        final_df[share_cols] = final_df[share_cols].apply(
            lambda x: pd.to_numeric(x.astype(str).str.replace(',', ''), errors='coerce') * 1000
        )
        # final_df.dropna(subset=['stock_id', 'foreign_buy_shares'], inplace=True) # 移除無效數據
        final_df = final_df[[
            'trade_date', 'stock_id', 
            'foreign_buy_shares', 'foreign_sell_shares', 
            'trust_buy_shares', 'trust_sell_shares', 
            'dealer_buy_shares', 'dealer_sell_shares'
        ]]
        # 儲存快取
        try:
            # Check if the file already exists
            if not os.path.exists(CACHE_PATH):
                os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
                # If file doesn't exist, write with header and index (initial write)
                final_df.to_csv(CACHE_PATH, mode='w', index=False, header=True, encoding="utf-8-sig")
                print(f"Created new file: {CACHE_PATH}")
            else:
                # If file exists, append without writing the header or index again
                final_df.to_csv(CACHE_PATH, mode='a', index=False, header=False, encoding="utf-8-sig")
                print(f"Appended data to existing file: {CACHE_PATH}")
            # final_df.to_csv(CACHE_PATH, mode='w', index=False, encoding="utf-8-sig")
        except Exception as e:
            print(f"⚠️ 寫入 institutional_investor 快取失敗：{e}")
    
        print(f"✅ combine_and_transform 完成，共 {len(final_df)} 筆")
        return final_df    
    

    def run_update(self, target_date: datetime.date = date.today()):
        """
        執行單日數據抓取、合併、轉換和寫入資料庫的主流程。
        """
        print(f"🚀 開始抓取 {target_date.strftime('%Y-%m-%d')} 三大法人數據...")
        
        twse_data = self.fetch_data_twse(target_date)
        tpex_data = self.fetch_data_tpex(target_date)
        
        final_data = self.combine_and_transform(twse_data, tpex_data)
        
        if final_data.empty:
            print(f"❌ 日期 {target_date.strftime('%Y-%m-%d')} 無有效法人交易數據，跳過寫入。")
            return

        # 寫入資料庫！
        save_institutional_data(final_data)
        
        print(f"✅ 成功抓取並寫入 {target_date.strftime('%Y-%m-%d')} {len(final_data)} 筆法人交易數據。")
        return final_data

    def load_from_cache() -> pd.DataFrame:
        """
        載入本地快取的三大法人交易清單（若不存在則回傳空 DataFrame）。
    
        Returns:
            pd.DataFrame: 快取內容或空表格。
        """
        CACHE_PATH = os.path.join("data", "institutional_investor.csv")
        
        if os.path.exists(CACHE_PATH):
            try:
                df = pd.read_csv(CACHE_PATH, dtype=str)
                return df
            except Exception as e:
                print(f"⚠️ 載入 hot_stocks 快取失敗：{e}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()


# 實作範例：
# fetcher = InstitutionalFetcher()
# data_to_write = fetcher.run_update() #datetime.date(2025, 12, 12)
# print('--------------------------------------------------')
# print(data_to_write)