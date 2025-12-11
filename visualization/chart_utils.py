"""
visualization/chart_utils.py
----------------
建立多股票技術技術指標繪圖功能，
包含 MA、RSI、MACD、BB、VOL。
"""

from utils.helpers import setup_logger
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

logger = setup_logger("chart_utils")

# -------------------------
# 收盤價 + 移動平均線
# -------------------------
def plot_price_ma(df: pd.DataFrame, stock_name: str, ma_columns=None):
    """
    收盤價 + 移動平均線
    df 必須包含: trade_date, close_price
    ma_columns: list of str, e.g. ["MA_5", "MA_20"]
    
    參數：
        df (pd.Dataframe): 股價資料
        stock_name (str): 股票名稱
        ma_columns (list): 均線基準
    
    返回型別：
        fig (go.Figure()): 圖表物件
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
    """
    RSI 指標圖(相對強弱指標)
    
    參數：
        df (pd.Dataframe): 股價資料
        stock_name (str): 股票名稱
    
    返回型別：
        fig (go.Figure()): 圖表物件
    """
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
    """
    MACD (指數平滑異同移動平均線)
    
    參數：
        df (pd.Dataframe): 股價資料
        stock_name (str): 股票名稱
    
    返回型別：
        fig (go.Figure()): 圖表物件
    """
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
    """
    Bollinger Bands (布林通道)
    
    參數：
        df (pd.Dataframe): 股價資料
        stock_name (str): 股票名稱
    
    返回型別：
        fig (go.Figure()): 圖表物件
    """
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
    """
    成交量 + 成交量均線
    
    參數：
        df (pd.Dataframe): 股價資料
        stock_name (str): 股票名稱
        ma_columns (list): 均線基準
    
    返回型別：
        fig (go.Figure()): 圖表物件
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


# -------------------------
# 資產的累積報酬率（淨值曲線）以及回撤深度
# -------------------------
def plot_cumulative_returns_and_drawdown(
    prices: pd.Series, 
    stock_name: str
) -> go.Figure:
    """
    繪製累積報酬率曲線與回撤深度圖。

    Args:
        prices (pd.Series): 帶有日期索引的價格序列 (e.g., 調整後的收盤價)。
        stock_name (str): 股票名稱。

    Returns:
        fig (go.Figure): 包含兩個子圖的圖表物件。
    """
    # 計算日報酬率
    returns = prices.pct_change()
    returns = returns.astype(float)
    # 計算累積報酬率 (從 1.0 開始)
    cumulative_returns = (1 + returns).cumprod().fillna(1)
    
    # 計算回撤深度
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns / running_max) - 1

    # 建立子圖：1 行 2 列，共兩個圖，共用 X 軸
    fig = make_subplots(
        rows=2, 
        cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.1,
        subplot_titles=(f"{stock_name} - 累積報酬率 (Cumulative Returns)", "回撤深度 (Drawdown Depth)"),
        row_heights=[0.7, 0.3] # 上方圖佔 70% 高度，下方佔 30%
    )

    # --- 第一個子圖：累積報酬率 ---
    fig.add_trace(
        go.Scatter(
            x=cumulative_returns.index, 
            y=cumulative_returns.values, 
            mode='lines', 
            name='累積報酬率',
            line=dict(color='blue')
        ),
        row=1, col=1
    )

    # --- 第二個子圖：回撤深度 ---
    # 標示最大回撤點
    max_dd_value = drawdown.min()
    fig.add_trace(
        go.Scatter(
            x=drawdown.index, 
            y=drawdown.values, 
            mode='lines', 
            name='回撤深度',
            fill='tozeroy',  # 填充到 Y=0 軸
            line=dict(color='red', width=0.5),
            hovertemplate='%{y:.2%}<extra></extra>' # 顯示為百分比
        ),
        row=2, col=1
    )
    # 標記 Max Drawdown 水平線
    fig.add_hline(y=max_dd_value, line_dash="dash", line_color="orange", 
                  annotation_text=f"Max DD: {max_dd_value:.2%}",
                  annotation_position="bottom right", row=2, col=1)

    # 調整佈局
    fig.update_layout(
        title_text=f"{stock_name} 績效分析",
        height=600,
        hovermode="x unified",
    )
    # 調整 Y 軸為百分比格式 (累積報酬率圖，如果需要)
    fig.update_yaxes(title_text="累積淨值", row=1, col=1)
    fig.update_yaxes(title_text="深度", tickformat=".0%", row=2, col=1)
    
    return fig