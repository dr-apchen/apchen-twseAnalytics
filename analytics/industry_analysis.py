# analytics/industry_analysis.py (修改)

import pandas as pd

class IndustryAnalyzer:
    # 移除 load_data() 函式，改為直接接收數據
    
    @staticmethod
    def calculate_industry_stock_returns(data_df: pd.DataFrame) -> pd.DataFrame:
        """
        計算該產業內所有股票的每日報酬率。
        
        Args:
            data_df: 特定產業在指定期間內所有股票的價格數據。
            
        Returns:
            pd.DataFrame: 包含 daily_return 欄位。
        """
        data_df['daily_return'] = data_df.groupby('stock_id')['close_price'].transform(
            lambda x: x.pct_change()
        )
        return data_df.dropna(subset=['daily_return'])

    @staticmethod
    def aggregate_industry_performance(data_with_returns: pd.DataFrame) -> pd.DataFrame:
        """
        計算單一產業的每日平均漲跌幅和總成交量。
        
        Args:
            data_with_returns: 包含 daily_return 的產業數據。
            
        Returns:
            pd.DataFrame: 每日產業聚合績效。
        """
        # 聚合計算：只根據 date 分組 (因為 industry 已經單一)
        daily_perf = data_with_returns.groupby('trade_date').agg(
            avg_return=('daily_return', 'mean'),  # 產業平均漲跌幅
            total_volume=('volume', 'sum'),       # 產業總成交量
            stock_count=('stock_id', 'count')     # 產業內股票數量
        ).reset_index()
        
        # 計算成交量變化
        daily_perf['volume_change_pct'] = daily_perf['total_volume'].pct_change()
        
        # 計算累積報酬率 (用日平均回報計算)
        daily_perf['cumulative_return'] = (1 + daily_perf['avg_return']).cumprod()

        return daily_perf
    
    @staticmethod
    def calculate_stock_total_returns(data_df: pd.DataFrame) -> pd.DataFrame:
        """
        計算產業內所有股票在整個時間區間的總報酬率。
        
        Args:
            data_df: 特定產業在指定期間內所有股票的價格數據 (包含 'close_price')。
            
        Returns:
            pd.DataFrame: 股票代碼和總報酬率 (Columns: stock_id, total_return)。
        """
        if data_df.empty:
            return pd.DataFrame(columns=['stock_id', 'total_return', 'industry'])
        
        # 找出每支股票在區間內的第一個收盤價 (Start Price) 和最後一個收盤價 (End Price)
        # 確保 trade_date 是日期格式
        data_df['trade_date'] = pd.to_datetime(data_df['trade_date'])
        
        summary = data_df.sort_values('trade_date').groupby('stock_id').agg(
            start_price=('close_price', 'first'),
            end_price=('close_price', 'last'),
            industry=('industry', 'first')
        ).reset_index()
        
        # 計算總報酬率: (期末價 - 期初價) / 期初價
        summary['total_return'] = (summary['end_price'] / summary['start_price']) - 1
        
        # 選擇需要的欄位並依報酬率排序
        ranking_df = summary[['stock_id', 'industry', 'total_return', 'start_price', 'end_price']].sort_values(
            by='total_return', 
            ascending=False
        )
        return ranking_df
    
    @staticmethod
    def get_top_bottom_n_stocks(ranking_df: pd.DataFrame, n: int = 5) -> list[str]:
        """
        從報酬率排行榜中，取得前 N 名和後 N 名的股票代碼列表。
        
        Args:
            ranking_df: 包含 stock_id 和 total_return 的數據框（已排序）。
            n: 欲篩選的數量。
            
        Returns:
            list[str]: 包含所有突顯股票代碼的列表。
        """
        if ranking_df.empty:
            return []
            
        # 由於 ranking_df 已經按 total_return 降冪排序
        top_n = ranking_df['stock_id'].head(n).tolist()
        
        # 取得報酬率最低的 N 檔 (從 DataFrame 尾部取)
        bottom_n = ranking_df['stock_id'].tail(n).tolist()
        
        return list(set(top_n + bottom_n))