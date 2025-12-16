# analytics/investor_flow_analysis.py

import pandas as pd
from data_collector.data_updater import load_foreign_net_buy # 載入外資淨買賣數據
from data_collector.data_updater import load_daily_all_institutional_data # 載入所有股票當日的法人數據，用於 Top N 排名
import datetime

class InvestorFlowAnalyzer:
    
    @staticmethod
    def calculate_cumulative_net_buy(net_buy_series: pd.Series) -> pd.Series:
        """
        計算外資的累積淨買入股數。
        
        Args:
            net_buy_series (pd.Series): 帶有日期索引的外資每日淨買入股數序列。
            
        Returns:
            pd.Series: 累積淨買入股數序列。
        """
        if net_buy_series.empty:
            return pd.Series(dtype='int64')
        return net_buy_series.cumsum()

    @staticmethod
    def get_top_n_net_buy_stocks(
        target_date: str, 
        n: int = 10 # 需要資料庫連接
    ) -> pd.DataFrame:
        """
        找出特定日期，外資淨買超股數最多的前 N 檔股票。
        
        Args:
            target_date (str): 查詢日期 (YYYY-MM-DD)。
            n (int): 欲篩選的數量。
            db_conn: 資料庫連接實例。
            
        Returns:
            pd.DataFrame: 包含 stock_id, foreign_net_shares, industry 的 Top N 列表。
        """
        
        # 1. 載入當日所有股票的法人淨買賣數據
        top_n_df = load_daily_all_institutional_data(target_date, n)
        # 這裡需要一個新的 data_loader 函式來載入所有股票的法人數據
        # 假設 load_daily_all_institutional_data(date, db_conn) 函式已存在
        # 並且能夠 join stock_info 獲取 industry 欄位
        
        if top_n_df.empty:
            print(f"日期 {target_date} 無外資淨買超 Top {n} 數據。")
            return pd.DataFrame(columns=['stock_id', 'foreign_net_shares', 'industry'])

        return top_n_df

    @staticmethod
    def analyze_top_n_trends(
        stock_ids: list[str], 
        start_date: str, 
        end_date: str # 需要資料庫連接
    ) -> pd.DataFrame:
        """
        追蹤 Top N 股票在過去一段時間的外資淨買賣超趨勢。
        
        Args:
            stock_ids (list[str]): 欲追蹤的股票代碼列表。
            start_date (str): 查詢起始日期。
            end_date (str): 查詢結束日期。
            db_conn: 資料庫連接實例。
            
        Returns:
            pd.DataFrame: 用於繪製圖表的數據 (trade_date, stock_id, foreign_net_shares)。
        """
        if not stock_ids:
            return pd.DataFrame()

        # 批量載入這些股票在指定區間的外資淨買賣超數據
        trend_data = load_foreign_net_buy(stock_ids, start_date, end_date)
        
        if trend_data.empty:
            print(f"找不到所選股票在 {start_date} 至 {end_date} 的外資交易趨勢數據。")
            return pd.DataFrame()
            
        trend_data['trade_date'] = pd.to_datetime(trend_data['trade_date'])
        
        return trend_data