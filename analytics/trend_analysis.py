"""
analytics/trend_analysis.py
-----------
趨勢分析模組
1. 從資料庫抓股價資料
2. 計算技術指標
3. 可輸出 DataFrame 或圖表（未來擴充）
"""

from utils.helpers import setup_logger
import pandas as pd

logger = setup_logger("trend_analysis")

def analyze_trend(df: pd.DataFrame):
    """
    自動趨勢分析解讀：
    - 收盤價 vs MA
    - RSI 超買/超賣
    - MACD 多空訊號
    - 成交量放大/縮小
    返回中文文字描述
    
    參數：
        df (pd.Dataframe): 股價資料
    
    返回：
        messages (str): 趨勢分析訊息
    """
    messages = []

    # 簡單 MA 趨勢
    if "MA_5" in df.columns and "MA_20" in df.columns:
        if df["MA_5"].iloc[-1] > df["MA_20"].iloc[-1]:
            messages.append("短期均線上穿長期均線 → 黃金交叉，多頭趨勢")
        elif df["MA_5"].iloc[-1] < df["MA_20"].iloc[-1]:
            messages.append("短期均線下穿長期均線 → 死亡交叉，空頭趨勢")
        else:
            messages.append("均線交錯，趨勢不明")

    # RSI 超買/超賣
    if "RSI" in df.columns:
        rsi = df["RSI"].iloc[-1]
        if rsi > 70:
            messages.append("RSI 超過 70 → 短期超買，股價可能回落")
        elif rsi < 30:
            messages.append("RSI 低於 30 → 短期超賣，股價可能反彈")

    # MACD 趨勢訊號
    if "MACD" in df.columns and "Signal" in df.columns:
        if df["MACD"].iloc[-1] > df["Signal"].iloc[-1]:
            messages.append("MACD 線上穿訊號線 → 多方訊號")
        elif df["MACD"].iloc[-1] < df["Signal"].iloc[-1]:
            messages.append("MACD 線下穿訊號線 → 空方訊號")

    # 成交量趨勢
    if "volume" in df.columns and "volume_MA5" in df.columns:
        vol = df["volume"].iloc[-1]
        vol_ma = df["volume_MA5"].iloc[-1]
        if vol > vol_ma:
            messages.append("成交量大於 5 日均線 → 趨勢強勁")
        else:
            messages.append("成交量小於 5 日均線 → 趨勢可能乏力")

    return messages
