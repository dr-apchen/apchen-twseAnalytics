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
import random

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


def plot_industry_cumulative_return(
    data_with_returns: pd.DataFrame, 
    industry_daily_perf: pd.DataFrame,
    stock_ranking_df: pd.DataFrame, # 個股總報酬率排行榜
    n_highlight: int = 5            # 突顯的數量
) -> go.Figure:
    """
    繪製單一產業內所有股票的累積報酬率，並疊加產業平均累積報酬率。

    Args:
        data_with_returns (pd.DataFrame): 包含個股日報酬率 ('daily_return') 的數據。
        industry_daily_perf (pd.DataFrame): 包含產業平均累積報酬率 ('cumulative_return') 的數據。
        stock_ranking_df (pd.DataFrame): 個股總報酬率排行榜
        n_highlight (int) = 5: 突顯的數量

    Returns:
        fig (go.Figure): 圖表物件。
    """
    if data_with_returns.empty or industry_daily_perf.empty:
        return go.Figure().update_layout(title="無數據可供繪製")

    industry_name = data_with_returns['industry'].iloc[0]
    
    # 1. 計算個股累積報酬率
    data_with_returns['trade_date'] = pd.to_datetime(data_with_returns['trade_date'])
    
    # 計算累積報酬率，並將結果儲存在一個新的 DataFrame 中
    
    # 建立一個包含 stock_id, trade_date, daily_return 的數據副本，確保操作不影響原始 df 
    temp_df = data_with_returns[['stock_id', 'trade_date', 'daily_return']].copy()
    
    # 設置索引方便計算
    temp_df = temp_df.set_index('trade_date').sort_index()

    # 使用 groupby 算出累積報酬率
    stock_cumulative_returns = temp_df.groupby('stock_id')['daily_return'].apply(
        lambda x: (1 + x).cumprod()
    ).reset_index() # <-- 使用 reset_index() 將 stock_id, trade_date 變回欄位
    
    # 重新命名累積報酬率的欄位
    stock_cumulative_returns.rename(
        columns={'daily_return': 'cumulative_return_stock'},
        inplace=True
    )

    # 準備繪圖用的 Pivot Table
    # 直接對包含所有必要欄位的 stock_cumulative_returns 進行 pivot 操作
    data_for_plot = stock_cumulative_returns.pivot_table(
        index='trade_date',
        columns='stock_id',  # <-- 現在 stock_id 是一個欄位，可以正確引用
        values='cumulative_return_stock'
    )
    

    # --- 篩選 Top/Bottom N 股票代碼 ---
    from analytics.industry_analysis import IndustryAnalyzer
    highlight_stocks = IndustryAnalyzer.get_top_bottom_n_stocks(stock_ranking_df, n=n_highlight)
    
    fig = go.Figure()
    
    # 2. 繪製所有個股的累積報酬率
    for stock_id in data_for_plot.columns:
        
        is_highlighted = stock_id in highlight_stocks
        
        if is_highlighted:
            # --- Top/Bottom N 突顯線條 ---
            # 獲取領漲股的集合
            top_n_stocks = stock_ranking_df.head(n_highlight)['stock_id'].values
            
            if stock_id in top_n_stocks:
                # 領漲股 (前 N 名)
                line_color = "green"  # 鮮綠色
                line_name_prefix = '領漲'
            else:
                # 落後股 (後 N 名)
                line_color = "red" # 鮮紅色
                line_name_prefix = '落後'

            # --- 突顯線條設定 ---
            line_width = 1.5 # 將線條加粗，更易於觀察
            line_name = f'{line_name_prefix}: {stock_id}'
            show_legend = True
            
        else:
            # --- 其餘個股背景線條 (Spaghetti Plot 解決方案) ---
            line_color = 'rgba(150, 150, 150, 0.5)' # 淺灰色，高透明度
            line_width = 1
            line_name = f'{stock_id}'
            show_legend = False # 關鍵：移除圖例項目

        fig.add_trace(
            go.Scatter(
                x=data_for_plot.index,
                y=data_for_plot[stock_id],
                mode='lines',
                name=line_name,
                line=dict(color=line_color, width=line_width),
                hoverinfo='name+y',
                showlegend=show_legend # 控制圖例顯示
            )
        )

    # 3. 繪製產業平均累積報酬率 (使用粗體、深色作為主線)
    # 確保 trade_date 也是索引
    industry_daily_perf = industry_daily_perf.set_index('trade_date').sort_index()
    
    fig.add_trace(
        go.Scatter(
            x=industry_daily_perf.index,
            y=industry_daily_perf['cumulative_return'],
            mode='lines',
            name=f'{industry_name} 產業平均',
            line=dict(color='blue', width=1.5),
            hovertemplate='日期: %{x}<br>平均累積報酬: %{y:.2f}<extra></extra>',
            showlegend=True # 確保主線條顯示在圖例中
        )
    )

    # 4. 調整佈局
    fig.update_layout(
        title={
            'text': f'{industry_name} 產業累積報酬率趨勢 (與個股比較)',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title="日期",
        yaxis_title="累積淨值 (基期=1.0)",
        height=600,
        hovermode="closest",
        legend_title="圖例 (點擊隱藏/顯示)",
        legend=dict(
            orientation="v",  # 水平排列
            yanchor="top",
            y=1,
            xanchor="left",
            x=1
        )
    )
    # 將 Y 軸起始點設為 1.0 (或接近 1.0 的值)
    fig.update_yaxes(rangemode='tozero', tickformat=".2f")
    
    return fig