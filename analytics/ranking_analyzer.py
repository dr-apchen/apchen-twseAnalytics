# analytics/ranking_analyzer.py

import pandas as pd
import datetime

class RankingAnalyzer:
    
    # ------------------------------------------------------------------------
    # 1. 個股日排名 (Daily Ranking) - daily_return 在 Python 中計算
    # ------------------------------------------------------------------------
    @staticmethod
    def get_stock_daily_ranking(
        conn,
        target_date: str, 
        metric: str, 
        n: int = 20
    ) -> pd.DataFrame:
        """
        載入特定日期、特定指標（漲跌幅或成交量）的個股 Top N 排行榜。
        
        Args:
            target_date (str): 查詢日期 (YYYY-MM-DD)。
            metric (str): 排行指標 ('daily_return' 或 'volume')。
        """
        
        if not conn:
            raise ValueError("需要提供資料庫連接實例。")
        cursor = conn.cursor()
        
        if metric not in ['daily_return', 'volume']:
            raise ValueError("metric 參數必須是 'daily_return' 或 'volume'。")

        order_direction = 'DESC'
        if metric == 'daily_return':
            # --- 策略：在 Python 中計算每日報酬率 ---
            
            # 1. 獲取目標日期和前一交易日的收盤價數據 (為了確保找到前一天的價格，向前多取幾天)
            # 實際交易日可能間隔幾天，所以我們向前回溯 5 個日曆日作為安全範圍
            days_back = (datetime.datetime.strptime(target_date, '%Y-%m-%d').date() - datetime.timedelta(days=5)).strftime('%Y-%m-%d')
            
            query = f"""
            SELECT 
                sdd.stock_id,
                sdd.trade_date,
                sdd.close_price,
                si.stock_name,
                si.industry
            FROM 
                stock_price_daily sdd
            LEFT JOIN 
                stock_info si ON sdd.stock_id = si.stock_id
            WHERE 
                sdd.trade_date BETWEEN %s AND %s
            ORDER BY
                sdd.trade_date ASC;
            """
            params = (days_back, target_date)
            cursor.execute(query, params)
            all_price_df = cursor.fetchall()
            columns = [
                'stock_id', 
                'trade_date', 
                'close_price', 
                'stock_name', 
                'industry'
            ]
            all_price_df = pd.DataFrame(all_price_df, columns=columns)
            if all_price_df.empty:
                return pd.DataFrame()
            # 2. 在 Python (Pandas) 中計算 daily_return
            all_price_df['prev_close'] = all_price_df.groupby('stock_id')['close_price'].shift(1)
            all_price_df['daily_return'] = (all_price_df['close_price'] / all_price_df['prev_close']) - 1
            
            # 3. 篩選目標日期的結果並排序
            ranking_df = all_price_df[all_price_df['trade_date'] == datetime.datetime.strptime(target_date, '%Y-%m-%d').date()]
            # 排除第一個交易日（daily_return 為 NaN）
            ranking_df = ranking_df.dropna(subset=['daily_return'])             
            ranking_df = ranking_df.sort_values(by='daily_return', ascending=False).head(n)            
            ranking_df.rename(columns={'daily_return': metric}, inplace=True)
            return ranking_df[['stock_id', 'stock_name', 'industry', metric]]

        else: # metric == 'volume'
            # 對於 volume，直接查詢即可 (欄位在資料表中實體儲存)
            query = f"""
            SELECT 
                sdd.stock_id,
                si.stock_name,
                si.industry,
                sdd.{metric} AS metric_value 
            FROM 
                stock_price_daily sdd
            LEFT JOIN 
                stock_info si ON sdd.stock_id = si.stock_id
            WHERE 
                sdd.trade_date = %s
            ORDER BY 
                metric_value {order_direction}
            LIMIT %s;
            """
            params = (target_date, n)
            cursor.execute(query, params)
            ranking_df = cursor.fetchall()
            columns = [
                'stock_id', 
                'stock_name', 
                'industry', 
                'metric_value'
            ]
            
            ranking_df = pd.DataFrame(ranking_df, columns=columns)
            ranking_df.rename(columns={'metric_value': metric}, inplace=True)
            return ranking_df[['stock_id', 'stock_name', 'industry', metric]]

        cursor.close()
    
    # ------------------------------------------------------------------------
    # 2. 產業日排名 (Industry Daily Ranking) - daily_return 在 SQL 中計算
    # ------------------------------------------------------------------------
    @staticmethod
    def get_industry_daily_ranking(
        conn,
        target_date: str, 
        n: int = 10
    ) -> pd.DataFrame:
        """
        計算並載入特定日期的產業平均漲跌幅 Top N 排行榜 (熱門產業)。
        
        ⚠️ 注意：此處使用 SQL 視窗函數 LAG() 進行即時計算。
        """
        
        if not conn:
            raise ValueError("需要提供資料庫連接實例。")
        cursor = conn.cursor()

        # 這裡需要查詢到 target_date 及其前一交易日的所有數據。
        # 由於我們只關心 target_date 的結果，所以 CTE 查詢範圍可設得寬一些。
        
        query = """
        WITH DailyReturns AS (
            SELECT 
                sdd.stock_id,
                sdd.trade_date,
                si.industry,
                sdd.close_price,
                -- 【關鍵】使用 LAG() 獲取前一筆交易日的收盤價，按 stock_id 分組
                LAG(sdd.close_price, 1) OVER (PARTITION BY sdd.stock_id ORDER BY sdd.trade_date) AS prev_close_price
            FROM 
                stock_price_daily sdd
            JOIN 
                stock_info si ON sdd.stock_id = si.stock_id
            WHERE 
                sdd.trade_date <= %s -- 查詢到目標日期的所有數據
        ),
        CalculatedReturns AS (
            SELECT
                trade_date,
                industry,
                (close_price - prev_close_price) / prev_close_price AS daily_return
            FROM DailyReturns
            WHERE prev_close_price IS NOT NULL
        )
        SELECT 
            industry,
            AVG(daily_return) AS average_daily_return
        FROM 
            CalculatedReturns
        WHERE
            trade_date = %s -- 只計算目標日期的平均值
        GROUP BY 
            industry
        ORDER BY 
            average_daily_return DESC
        LIMIT %s;
        """
        
        params = (target_date, target_date, n) 
        
        try:
            cursor.execute(query, params)
            ranking_df = cursor.fetchall()
            columns = [
                'industry',
                'average_daily_return'
            ]
            
            ranking_df = pd.DataFrame(ranking_df, columns=columns)
            return ranking_df
        except Exception as e:
            # 
            print(f"獲取產業排名數據時發生錯誤。請確認您的資料庫支援 LAG() 視窗函數：{e}")
            return pd.DataFrame(columns=['industry', 'average_daily_return'])
        finally:
            cursor.close()


    # ------------------------------------------------------------------------
    # 3. 區間排名 (Period Ranking) - 累積報酬率和總成交量
    # ------------------------------------------------------------------------
    @staticmethod
    def get_stock_period_ranking(
        conn,
        start_date: str,
        end_date: str,
        metric: str,
        n: int = 20
    ) -> pd.DataFrame:
        """
        載入特定期間、特定指標（累積報酬率或總成交量）的個股 Top N 排行榜。
        
        ⚠️ 注意：累積報酬率 metric='cumulative_return' 使用每日報酬率的總和作為近似值。
        """
        if not conn:
            raise ValueError("需要提供資料庫連接實例。")
        cursor = conn.cursor()
        
        if metric not in ['cumulative_return', 'total_volume']:
            raise ValueError("metric 參數必須是 'cumulative_return' 或 'total_volume'。")
            
        if metric == 'total_volume':
            # 對於 total_volume，由於 volume 是實體欄位，SQL 聚合仍然可行
            query = f"""
            SELECT 
                sdd.stock_id,
                si.stock_name,
                si.industry,
                SUM(sdd.volume) AS metric_value 
            FROM 
                stock_price_daily sdd
            LEFT JOIN 
                stock_info si ON sdd.stock_id = si.stock_id
            WHERE 
                sdd.trade_date BETWEEN %s AND %s
            GROUP BY 
                sdd.stock_id, si.stock_name, si.industry
            ORDER BY 
                metric_value DESC
            LIMIT %s;
            """
            params = (start_date, end_date, n)
            
            cursor.execute(query, params)
            ranking_data_list = cursor.fetchall()
            cursor.close()
            # ... (後續 DataFrame 轉換和返回邏輯保持不變) ...
            
            if not ranking_data_list:
                return pd.DataFrame(columns=['stock_id', 'stock_name', 'industry', metric])

            columns = ['stock_id', 'stock_name', 'industry', 'metric_value'] 
            ranking_df = pd.DataFrame(ranking_data_list, columns=columns)
            ranking_df.rename(columns={'metric_value': metric}, inplace=True)
            return ranking_df[['stock_id', 'stock_name', 'industry', metric]]
            
        elif metric == 'cumulative_return':
            # --- 策略：在 Python 中計算累積報酬率 (SUM daily_return) ---
            
            # 1. 擴大 SQL 查詢：查詢區間內所有原始價格數據
            # 為了計算區間第一天的 daily_return，需再往前多查詢幾天
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            days_back = (start_date - datetime.timedelta(days=5)).strftime('%Y-%m-%d')

            query = f"""
            SELECT 
                sdd.stock_id,
                sdd.trade_date,
                sdd.close_price
            FROM 
                stock_price_daily sdd
            WHERE 
                sdd.trade_date BETWEEN %s AND %s
            ORDER BY
                sdd.trade_date ASC;
            """
            params = (days_back, end_date)
            
            cursor.execute(query, params)
            raw_data_list = cursor.fetchall()
            
            if not raw_data_list:
                return pd.DataFrame()

            # 2. Python/Pandas 處理：計算 daily_return
            price_df = pd.DataFrame(raw_data_list, columns=['stock_id', 'trade_date', 'close_price'])
            price_df['prev_close'] = price_df.groupby('stock_id')['close_price'].shift(1)
            price_df['daily_return'] = (price_df['close_price'] / price_df['prev_close']) - 1
            
            # 3. 篩選有效區間數據 (從 start_date 到 end_date)
            period_df = price_df[
                (price_df['trade_date'] >= start_date) & 
                (price_df['trade_date'] <= end_date)
            ]
            
            # 4. Python/Pandas 聚合：計算累積報酬率 (SUM daily_return)
            ranking_df = period_df.groupby('stock_id')['daily_return'].sum().reset_index()
            ranking_df.rename(columns={'daily_return': metric}, inplace=True)
            
            # 5. 結合股票資訊
            cursor.execute("SELECT stock_id, stock_name, industry FROM stock_info")
            stock_info_df = cursor.fetchall()
            cursor.close()
            
            stock_info_df = pd.DataFrame(stock_info_df, columns=['stock_id', 'stock_name', 'industry'])            
            final_ranking = pd.merge(ranking_df, stock_info_df, on='stock_id', how='left')
            
            # 6. 排序和限制 Top N
            final_ranking = final_ranking.sort_values(by=metric, ascending=False).head(n)
            
            return final_ranking[['stock_id', 'stock_name', 'industry', metric]]