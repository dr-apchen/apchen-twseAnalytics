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
    """
    計算移動平均 (MA)
    
    參數：
        df (pd.Dataframe): 股價資料
        column (str): 預設欄位
        windows (list): 均線基準
    
    返回：
        df (pd.Dataframe): 數據計算結果
    """
    for w in windows:
        df[f"MA_{w}"] = df[column].rolling(w).mean()
    return df

# -------------------------
# 計算 RSI
# -------------------------
def calculate_rsi(df: pd.DataFrame, column: str = "close_price", period: int = 14):
    """
    計算 RSI (相對強弱指標)
    
    參數：
        df (pd.Dataframe): 股價資料
        column (str): 預設欄位
        period (int): 期間
    
    返回：
        df (pd.Dataframe): 數據計算結果
    """
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
    """
    計算 MACD (指數平滑異同移動平均線)
    
    參數：
        df (pd.Dataframe): 股價資料
        column (str): 預設欄位
        fast (int): 預設參數
        slow (int): 預設參數
        signal (int): 預設參數
    
    返回：
        df (pd.Dataframe): 數據計算結果
    """
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
    """
    計算 Bollinger Bands (布林通道)
    
    參數：
        df (pd.Dataframe): 股價資料
        column (str): 預設欄位
        window (int): 預設參數
        num_std (int): 預設參數
    
    返回：
        df (pd.Dataframe): 數據計算結果
    """
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
    """
    計算成交量均線
    
    參數：
        df (pd.Dataframe): 股價資料
        column (str): 預設欄位
        window (list): 預設參數
    
    返回：
        df (pd.Dataframe): 數據計算結果
    """
    for w in windows:
        df[f"{column}_MA{w}"] = df[column].rolling(w).mean()
    return df

# -------------------------
# 整合計算函數
# -------------------------
def calculate_all_indicators(df: pd.DataFrame):
    """
    計算所有技術指標
    
    參數：
        df (pd.Dataframe): 股價資料
    
    返回：
        df (pd.Dataframe): 數據計算結果
    """
    df = calculate_ma(df)
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_bollinger_bands(df)
    df = calculate_volume_ma(df)
    return df
