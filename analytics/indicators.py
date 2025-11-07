"""
analytics/indicators.py
-----------
技術指標計算模組
包含 MA、RSI、MACD、BB、VOL
"""

from utils.helpers import setup_logger
import pandas as pd

logger = setup_logger("indicators")

# -------------------------
# 計算移動平均線
# -------------------------
def calculate_ma(df: pd.DataFrame, column: str = "close_price", windows=[5, 20]):
    """TODO: Add docstring for def calculate_ma(df: pd.DataFrame, column: str = "close_price", windows=[5, 20]):"""
    for w in windows:
        df[f"MA_{w}"] = df[column].rolling(w).mean()
    return df

# -------------------------
# 計算 RSI
# -------------------------
def calculate_rsi(df: pd.DataFrame, column: str = "close_price", period: int = 14):
    """TODO: Add docstring for def calculate_rsi(df: pd.DataFrame, column: str = "close_price", period: int = 14):"""
    delta = df[column].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

# -------------------------
# 計算 MACD
# -------------------------
def calculate_macd(df: pd.DataFrame, column: str = "close_price", fast=12, slow=26, signal=9):
    """TODO: Add docstring for def calculate_macd(df: pd.DataFrame, column: str = "close_price", fast=12, slow=26, signal=9):"""
    df["EMA_fast"] = df[column].ewm(span=fast, adjust=False).mean()
    df["EMA_slow"] = df[column].ewm(span=slow, adjust=False).mean()
    df["MACD"] = df["EMA_fast"] - df["EMA_slow"]
    df["Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    df.drop(columns=["EMA_fast","EMA_slow"], inplace=True)
    return df

# -------------------------
# 計算 Bollinger Bands
# -------------------------
def calculate_bollinger_bands(df: pd.DataFrame, column: str = "close_price", window: int = 20, num_std: int = 2):
    """TODO: Add docstring for def calculate_bollinger_bands(df: pd.DataFrame, column: str = "close_price", window: int = 20, num_std: int = 2):"""
    df["BB_middle"] = df[column].rolling(window).mean()
    df["BB_std"] = df[column].rolling(window).std()
    df["BB_upper"] = df["BB_middle"] + num_std * df["BB_std"]
    df["BB_lower"] = df["BB_middle"] - num_std * df["BB_std"]
    df.drop(columns=["BB_std"], inplace=True)
    return df

# -------------------------
# 計算成交量均線
# -------------------------
def calculate_volume_ma(df: pd.DataFrame, column: str = "volume", windows=[5]):
    """TODO: Add docstring for def calculate_volume_ma(df: pd.DataFrame, column: str = "volume", windows=[5]):"""
    for w in windows:
        df[f"{column}_MA{w}"] = df[column].rolling(w).mean()
    return df

# -------------------------
# 整合計算函數
# -------------------------
def calculate_all_indicators(df: pd.DataFrame):
    """TODO: Add docstring for def calculate_all_indicators(df: pd.DataFrame):"""
    df = calculate_ma(df)
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_bollinger_bands(df)
    df = calculate_volume_ma(df)
    return df
