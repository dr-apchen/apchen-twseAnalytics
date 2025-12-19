"""
analytics/portfolio_stats.py
-----------
產生多股票技術指標摘要表 + 趨勢 + 建議
"""

from utils.helpers import setup_logger
import pandas as pd
from io import BytesIO
from analytics.trend_analysis import analyze_trend

logger = setup_logger("portfolio_stats")

def generate_summary_table(stock_data_dict):
    """
    多股票技術指標摘要表
    
    參數：
        stock_data_dict (dict): 股價資訊
    
    返回：
        df_summary (pd.Dataframe): 股價摘要
    """

    summary_rows = []

    for stock_id, (stock_name, df) in stock_data_dict.items():
        if df is None or df.empty:
            continue

        latest = df.iloc[-1]
        close = latest["close_price"]
        change = (
            (df["close_price"].iloc[-1] - df["close_price"].iloc[-2]) / df["close_price"].iloc[-2] * 100
            if len(df) > 1 else 0
        )

        ma5 = latest.get("MA_5", None)
        ma20 = latest.get("MA_20", None)
        rsi = latest.get("RSI", None)
        macd = latest.get("MACD", None)
        signal = latest.get("Signal", None)
        bb_upper = latest.get("BB_upper", None)
        bb_lower = latest.get("BB_lower", None)

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
            "收盤價": round(close, 2),
            "漲跌幅(%)": round(change, 2),
            "MA5": round(ma5, 2) if ma5 else None,
            "MA20": round(ma20, 2) if ma20 else None,
            "RSI": round(rsi, 2) if rsi else None,
            "RSI 狀態": rsi_status,
            "MACD": round(macd, 2) if macd else None,
            "MACD 訊號": macd_signal,
            "趨勢": trend_state,
            "建議": suggestion,
            "趨勢摘要": short_summary
        })

    df_summary = pd.DataFrame(summary_rows)
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
        df_summary.to_excel(writer, index=False, sheet_name="Stock Summary")
    return output.getvalue()
