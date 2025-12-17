"""
analytics/portfolio_stats.py
-----------
產生多股票技術指標摘要表 + 趨勢 + 建議
"""
from utils.helpers import setup_logger
import numpy as np
import pandas as pd
from io import BytesIO
from analytics.trend_analysis import analyze_trend

logger = setup_logger("portfolio_stats")

def calculate_daily_returns(prices: pd.Series) -> pd.Series:
    """
    計算價格序列的每日報酬率。
    
    Args:
        prices: 帶有日期索引的價格序列 (e.g., 調整後的收盤價)。
        
    Returns:
        每日報酬率序列。
    """
    # prices.pct_change() 會計算 (今價 - 昨價) / 昨價
    return prices.pct_change().dropna()

def calculate_annualized_return(returns: pd.Series, trading_days=252) -> float:
    """
    計算年化報酬率 (CAGR的近似值)。
    
    Args:
        returns: 每日報酬率序列。
        trading_days: 一年中的交易日數 (台灣約 252)。
        
    Returns:
        年化報酬率 (百分比表示的浮點數)。
    """
    mean_daily_return = returns.mean()
    # 幾何平均法 (更嚴謹的 CAGR 需計算期末/期初，這裡用日回報平均來近似)
    return (1 + mean_daily_return) ** trading_days - 1

def calculate_annualized_volatility(returns: pd.Series, trading_days=252) -> float:
    """
    計算年化標準差 (波動率)。
    
    Args:
        returns: 每日報酬率序列。
        trading_days: 一年中的交易日數 (台灣約 252)。
        
    Returns:
        年化波動率 (浮點數)。
    """
    returns = returns.astype(float)
    daily_stdev = returns.std()
    
    return daily_stdev * np.sqrt(trading_days)

def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    計算最大回撤 (Max Drawdown)。
    
    Args:
        prices: 價格序列或累積淨值序列。
        
    Returns:
        最大回撤 (負值表示的浮點數，例如 -0.25)。
    """
    # 1. 計算累積淨值
    cumulative_wealth = (1 + prices.pct_change().fillna(0)).cumprod()
    cumulative_wealth = cumulative_wealth.astype(float)
    # 2. 計算歷史最高點 (Peak)
    # expand.max() 是從序列開始到當前為止的最大值
    running_max = cumulative_wealth.expanding().max()
    running_max = running_max.astype(float)
    # 3. 計算當前回撤 (Drawdown)
    drawdown = (cumulative_wealth / running_max) - 1
    
    # 4. 找到最大回撤值
    max_drawdown = drawdown.min()
    
    return max_drawdown

def generate_summary_table(stock_data_dict):
    """
    多股票技術指標摘要表
    
    參數：
        stock_data_dict (dict): 股價資訊
    
    返回：
        df_summary (pd.Dataframe): 股價摘要
    """

    summary_rows = []
    performance_rows = []

    for stock_id, (stock_name, df) in stock_data_dict.items():
        if df is None or df.empty:
            continue

        latest = df.iloc[-1]
        close = latest["close_price"]
        change = (
            (df["close_price"].iloc[-1] - df["close_price"].iloc[-2]) / df["close_price"].iloc[-2] * 100
            if len(df) > 1 else 0
        )
        #指標
        ma5 = latest.get("MA_5", None)
        ma20 = latest.get("MA_20", None)
        rsi = latest.get("RSI", None)
        macd = latest.get("MACD", None)
        signal = latest.get("Signal", None)
        bb_upper = latest.get("BB_upper", None)
        bb_lower = latest.get("BB_lower", None)
        
        #每日報酬率、年化報酬率、最大回撤、波動率
        dr = calculate_daily_returns(df["close_price"])
        ar = calculate_annualized_return(dr)
        ar_percentage = (str(int(ar*100))+"%") if ar else None
        av = calculate_annualized_volatility(dr)
        av_percentage = (str(int(av*100))+"%") if av else None
        md = calculate_max_drawdown(df["close_price"])
        md_percentage = (str(int(md*100))+"%") if md else None
        
        
        
        # 趨勢狀態
        if ma5 and ma20:
            if ma5 > ma20:
                trend_state = "多頭"
            elif ma5 < ma20:
                trend_state = "空頭"
            else:
                trend_state = "盤整"
        else:
            trend_state = "未知"

        # RSI 解讀
        rsi_status = "正常"
        if rsi:
            if rsi < 30:
                rsi_status = "超賣"
            elif rsi > 70:
                rsi_status = "超買"

        # MACD 解讀
        macd_signal = ""
        if macd and signal:
            if macd > signal:
                macd_signal = "多方"
            elif macd < signal:
                macd_signal = "空方"
            else:
                macd_signal = "中性"

        # 綜合建議
        suggestion = "觀望"
        if trend_state == "多頭" and rsi_status != "超買" and macd_signal == "多方":
            suggestion = "✅ 買進"
        elif trend_state == "空頭" and rsi_status != "超賣" and macd_signal == "空方":
            suggestion = "⚠️ 賣出"

        # 自動文字分析摘要
        analysis_texts = analyze_trend(df)
        short_summary = analysis_texts[0] if analysis_texts else "無明顯趨勢"

        summary_rows.append({
            "股票代號": stock_id,
            "股票名稱": stock_name,
            "收盤價": "{:.2f}".format(round(close, 2)),
            "漲跌幅(%)": "{:.2f}".format(round(change, 2)),
            "MA5": "{:.2f}".format(round(ma5, 2)) if ma5 else None,
            "MA20": "{:.2f}".format(round(ma20, 2)) if ma20 else None,
            "RSI": "{:.2f}".format(round(rsi, 2)) if rsi else None,
            "RSI 狀態": rsi_status,
            "MACD": "{:.2f}".format(round(macd, 2)) if macd else None,
            "MACD 訊號": macd_signal,
            "趨勢": trend_state,
            "建議": suggestion,
            "趨勢摘要": short_summary
        })
        performance_rows.append({
            "股票代號": stock_id,
            "股票名稱": stock_name,
            "年化報酬率": ar_percentage,
            "波動率": av_percentage,
            "最大回撤": md_percentage
        })
    df_summary = {"summary": pd.DataFrame(summary_rows), "performance": pd.DataFrame(performance_rows)}
    
    return df_summary


def export_summary_to_excel(df_summary):
    """
    多股票技術指標摘要表匯出摘要表成 Excel 檔案
    
    參數：
        df_summary (pd.Dataframe): 股價摘要
    
    返回：
        output.getvalue()
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_summary["summary"].to_excel(writer, index=False, sheet_name="Stock Summary")
        df_summary["performance"].to_excel(writer, index=False, sheet_name="Performance Statistics")
    return output.getvalue()
