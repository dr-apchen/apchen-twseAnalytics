"""
visualization/chart_utils.py
----------------
建立多股票技術技術指標繪圖功能，
包含 MA、RSI、MACD、BB、VOL。
"""

from utils.helpers import setup_logger
import plotly.graph_objects as go
import pandas as pd

logger = setup_logger("chart_utils")

# -------------------------
# 收盤價 + 移動平均線
# -------------------------
def plot_price_ma(df: pd.DataFrame, stock_name: str, ma_columns=None):
    """TODO: Add docstring for def plot_price_ma(df: pd.DataFrame, stock_name: str, ma_columns=None):"""
    """
    df 必須包含: trade_date, close_price
    ma_columns: list of str, e.g. ["MA_5", "MA_20"]
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["close_price"],
        mode="lines", name="收盤價", line=dict(color="blue")
    ))

    if ma_columns:
        colors = ["orange", "green", "purple", "red"]
        for i, ma in enumerate(ma_columns):
            if ma in df.columns:
                days = ma.split("_")[1]  # 例如 MA_5 -> 5
                fig.add_trace(go.Scatter(
                    x=df["trade_date"], y=df[ma],
                    mode="lines", name=f"{days} 日均線", line=dict(color=colors[i % len(colors)])
                ))

    fig.update_layout(
        title=f"{stock_name} 收盤價與移動平均線",
        xaxis_title="日期",
        yaxis_title="價格"
    )
    return fig

# -------------------------
# RSI 指標圖
# -------------------------
def plot_rsi(df: pd.DataFrame, stock_name: str):
    """TODO: Add docstring for def plot_rsi(df: pd.DataFrame, stock_name: str):"""
    if "RSI" not in df.columns:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["RSI"],
        mode="lines", name="RSI 指標", line=dict(color="purple")
    ))
    fig.update_layout(
        title=f"{stock_name} RSI 指標",
        xaxis_title="日期",
        yaxis=dict(range=[0, 100])
    )
    return fig

# -------------------------
# MACD 指標圖
# -------------------------
def plot_macd(df: pd.DataFrame, stock_name: str):
    """TODO: Add docstring for def plot_macd(df: pd.DataFrame, stock_name: str):"""
    if "MACD" not in df.columns or "Signal" not in df.columns:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["MACD"],
        mode="lines", name="MACD", line=dict(color="red")
    ))
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["Signal"],
        mode="lines", name="MACD 訊號線", line=dict(color="blue")
    ))
    fig.update_layout(
        title=f"{stock_name} MACD 指標",
        xaxis_title="日期",
        yaxis_title="MACD"
    )
    return fig

# -------------------------
# Bollinger Bands
# -------------------------
def plot_bollinger_bands(df: pd.DataFrame, stock_name: str):
    """TODO: Add docstring for def plot_bollinger_bands(df: pd.DataFrame, stock_name: str):"""
    if not all(col in df.columns for col in ["BB_upper", "BB_middle", "BB_lower"]):
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["trade_date"], y=df["close_price"], mode="lines", name="收盤價", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df["trade_date"], y=df["BB_upper"], mode="lines", name="上軌", line=dict(color="red")))
    fig.add_trace(go.Scatter(x=df["trade_date"], y=df["BB_middle"], mode="lines", name="中軌", line=dict(color="orange")))
    fig.add_trace(go.Scatter(x=df["trade_date"], y=df["BB_lower"], mode="lines", name="下軌", line=dict(color="green")))

    fig.update_layout(
        title=f"{stock_name} Bollinger Bands",
        xaxis_title="日期",
        yaxis_title="價格"
    )
    return fig

# -------------------------
# 成交量 + 成交量均線
# -------------------------
def plot_volume(df: pd.DataFrame, stock_name: str, ma_volume: str = None):
    """TODO: Add docstring for def plot_volume(df: pd.DataFrame, stock_name: str):"""
    """
    df 必須包含: trade_date, volume
    ma_volume: 成交量均線欄位名稱
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["trade_date"], y=df["volume"], name="成交量", marker_color="blue"
    ))
    if ma_volume and ma_volume in df.columns:
        # 將欄位名稱 volume_MA5 轉換成「成交量 5 日均線」
        if ma_volume.startswith("volume_MA"):
            days = ma_volume.split("MA")[1]
            name = f"成交量 {days} 日均線"
        else:
            name = ma_volume
            
        fig.add_trace(go.Scatter(
            x=df["trade_date"], y=df[ma_volume], mode="lines", name=name, line=dict(color="orange")
        ))

    fig.update_layout(
        title=f"{stock_name} 成交量",
        xaxis_title="日期",
        yaxis_title="成交量"
    )
    return fig