"""
visualization/dashboard.py
-------------
主視覺化儀表板模組（Streamlit）。

此模組整合股價分析視覺化、技術指標圖表顯示，
並新增「熱門股票清單」功能，供使用者快速選取熱門標的進行分析。
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from analytics.trend_analysis import analyze_trend
from analytics.indicators import calculate_all_indicators
from utils.stock_info_map import get_stock_name
from visualization.summary_table import build_summary_table
from visualization.chart_utils import (
    plot_price_ma,
    plot_rsi,
    plot_macd,
    plot_bollinger_bands,
    plot_volume,
)
from data_collector.data_updater import (
    fetch_and_store,
    check_stock_data_exists,
    load_stock_data,
)
from data_collector.hot_stock_fetcher import (
    merge_and_save_hot_stocks,
    load_hot_stocks_from_cache,
)
from utils.helpers import setup_logger

# 假設 data_loader 已配置好
from analytics.portfolio_stats import (
    calculate_annualized_return, 
    calculate_annualized_volatility, 
    calculate_max_drawdown
)
from visualization.chart_utils import plot_cumulative_returns_and_drawdown # 引入新圖表函式


logger = setup_logger("dashboard")

def ensure_data_completeness(stock_id: str, start_date: str, end_date: str):
    """
    檢查資料是否完整，若缺少日期範圍內的最新資料則自動抓取補齊。
    
    參數：
        stock_id (str): : 股票代碼
        start_date (str): 查詢起始日期
        end_date (str): 查詢結束日期
    
    返回：
        df (pd.Dataframe): 股價資料
    """
    # Step 1: 自動補抓缺資料
    exists = check_stock_data_exists(stock_id, start_date, end_date)
    if not exists:
        print(f"⚠️ 資料庫中無 {stock_id} 資料，自動抓取中...")
        fetch_and_store(stock_id, start_date, end_date)

        # schedule.every().day.at("09:00").do(daily_task, stock_id=stock_id)
        # print(f"⏰ 已設定每日 9:00 自動抓取 {stock_id} 資料並更新技術指標")

    # Step 2: 讀取資料庫
    df = load_stock_data(stock_id, start_date, end_date)
    
    if df.empty:
        st.error(f"❌ 抓取 {stock_id} 資料失敗，請檢查股票代碼或網路連線")
        
    # Step 3: 偵測資料庫缺口
    else:
        latest_date_in_db = df["trade_date"].max().date()
        if type(start_date) is str:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if type(end_date) is str:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
        # 若資料未涵蓋至結束日期，則補抓缺口
        if latest_date_in_db < end_date:
            missing_start = latest_date_in_db + timedelta(days=1)
            st.info(f"📥 發現 {stock_id} 資料缺少 {missing_start} 到 {end_date}，自動補抓中...")
            fetch_and_store(stock_id, missing_start, end_date)
            df = load_stock_data(stock_id, start_date, end_date)
        
    return df

def run_dashboard():
    """
    顯示頁面內容，可選擇分析模式：個股分析、多股票摘要表
    
    參數：
        NA
    
    返回：
        NA
    """

    st.set_page_config(page_title="股市分析平台", layout="wide")
    st.title("📈 動態股市分析平台 (台股上市上櫃)")
    
    # 取得使用者模式選擇
    st.sidebar.header("🔍 功能選單")
    mode = st.sidebar.radio("選擇分析模式：", ["個股分析", "多股票摘要表"])        
    # 共用日期範圍    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.sidebar.date_input("📆 開始日期", datetime(2023, 1, 1))
    with col2:    
        end_date = st.sidebar.date_input("📆 結束日期", datetime.today() - timedelta(days=1))
        
    # ================================
    # 模式一：個股分析
    # ================================
    if mode == "個股分析":
        default_stock_id = hot_stock_fetcher()
        stock_id = st.sidebar.text_input("📊 請輸入股票代號（例如：2330）", value=default_stock_id)

        if stock_id:
            # -----------------------------
            # 自動抓取股票名稱
            # -----------------------------
            stock_name = get_stock_name(stock_id)
            st.subheader(f"{stock_name}（{stock_id}） 技術分析")
        
            # -----------------------------
            # 讀取資料庫
            # -----------------------------
            df = ensure_data_completeness(stock_id, start_date, end_date)
        
            if df.empty:
                return
            
            else:
                # 計算技術指標
                df = calculate_all_indicators(df)
                generate_charts(df, stock_name)  
                
                # 取得資料更新時間
                latest_date = df["trade_date"].max()
                st.caption(f"📅 資料更新至：{latest_date.strftime('%Y-%m-%d')}")


    # ================================
    # 模式二：多股票摘要表
    # ================================
    elif mode == "多股票摘要表":
        # -----------------------------
        # 使用者輸入股票代碼
        # -----------------------------
        st.sidebar.subheader("📋 輸入多支股票代號")
        stock_input = st.sidebar.text_area("輸入多個股票代號，以逗號分隔（例如：2330, 2317, 2303）")
        stock_ids = [s.strip() for s in stock_input.split(",") if s.strip()]
        
        if not stock_ids or len(stock_ids) <= 1:
            st.info("💡 請在左側輸入至少兩個股票代號。")
            return

        stock_data_dict = {}
        for stock_id in stock_ids:
            stock_name = get_stock_name(stock_id)
            df = ensure_data_completeness(stock_id, start_date, end_date)
            if df.empty:
                return
            
            if not df.empty:
                df = calculate_all_indicators(df)
                stock_data_dict[stock_id] = (stock_name, df)
                generate_charts(df, stock_name)                    

        if not stock_data_dict:
            st.error("❌ 無法取得任何股票資料，請確認代號是否正確。")
            return
        else:
            # -------------------------
            # 顯示多股票技術指標摘要表
            # -------------------------
            st.markdown("## 📊 多股票技術指標摘要表")
            build_summary_table(stock_data_dict)
            
        # 自動偵測資料最新日期
        all_dates = [df[1]["trade_date"].max() for df in stock_data_dict.values()]
        latest_update = max(all_dates) if all_dates else "未知"
        st.caption(f"📅 資料更新至：{latest_update.strftime('%Y-%m-%d')}")
                        
            
    st.sidebar.markdown("---")
    st.sidebar.markdown("**版本**： Beta 1.0")
            
def generate_charts(df: pd.DataFrame, stock_name: str):
    """
    檢查資料是否完整，若缺少日期範圍內的最新資料則自動抓取補齊。
    
    參數：
        df (pd.Dataframe): 股價資料
        stock_name (str): 股票名稱
    
    返回：
        NA
    """

    # -------------------------
    # 自動趨勢分析解讀
    # -------------------------
    trend_messages = analyze_trend(df)
    if trend_messages:
        st.markdown(f"### 🔔 {stock_name} 趨勢分析解讀")
        for msg in trend_messages:
            st.info(msg)

    # 個股圖表展示
    # -------------------------
    # 繪圖
    # -------------------------
    with st.expander(f"📊 {stock_name} 詳細圖表", expanded=False):
        # -----------------------------
        # 收盤價 + MA
        # -----------------------------
        fig_price = plot_price_ma(df, stock_name, ["MA_5", "MA_20"])
        if fig_price: st.plotly_chart(fig_price, use_container_width=True)

        # -----------------------------
        # RSI
        # -----------------------------
        if "RSI" in df.columns:
            fig_rsi = plot_rsi(df, stock_name)
            if fig_rsi: st.plotly_chart(fig_rsi, use_container_width=True)

        # -----------------------------
        # MACD
        # -----------------------------
        if "MACD" in df.columns and "Signal" in df.columns:
            fig_macd = plot_macd(df, stock_name)
            if fig_macd: st.plotly_chart(fig_macd, use_container_width=True)


        # -----------------------------
        # RSI
        # -----------------------------
        if "RSI" in df.columns:
            fig_bb = plot_bollinger_bands(df, stock_name)
            if fig_bb: st.plotly_chart(fig_bb, use_container_width=True)
        
        # -----------------------------
        # VOL
        # -----------------------------
        fig_vol = plot_volume(df, stock_name, ma_volume="volume_MA5")
        fig_vol.data[1].name = "成交量 5 日均線"
        if fig_vol: st.plotly_chart(fig_vol, use_container_width=True) 
    
    # 假設在 Streamlit 的主要運行邏輯中呼叫：
    if df is not None:
        render_performance_metrics(df, stock_name)
    
    
    
def hot_stock_fetcher() -> str:
    """
    熱門股清單載入
    
    參數：
        NA
    
    返回：
        str
    """
    # 🔥 熱門股票區塊
    LIMIT_NUM = 10
    hot_df = load_hot_stocks_from_cache()
    if hot_df.empty:
        hot_df = merge_and_save_hot_stocks(limit=LIMIT_NUM)
        
    if not hot_df.empty:
        hot_df = hot_df.head(LIMIT_NUM)
        stock_hot = st.sidebar.selectbox(
            "選擇熱門股票", [""] + [f"{r.StockName}（{r.StockID}）" for _, r in hot_df.iterrows()]
        )
        if stock_hot:
            stock_id = stock_hot.split("（")[1].replace("）", "")
            st.session_state["selected_stock"] = stock_id
            
        st.session_state.caption_message = f"📅 熱門股更新至：{hot_df['UpdateTime'][0]}"
        hot_stock_fetcher_update(LIMIT_NUM)    
        
        
    # 若使用者已選熱門股則帶入
    selected_stock = st.session_state.get("selected_stock", "")
    return selected_stock
    # print(selected_stock)    
    
def hot_stock_fetcher_update(limit: int = 10):
    """
    熱門股清單更新
    
    參數：
        limit (int): 筆數 (預設10)
    
    返回：
        NA
    """
    # 1. 初始化 session_state
    if 'caption_message' not in st.session_state:
        st.session_state.caption_message = f"📅 熱門股更新至..."
    if 'counter' not in st.session_state:
        st.session_state.counter = 0
        
    # 2. 創建側邊欄的佔位符
    # 我們使用一個佔位符來容納 st.caption，這樣我們就可以隨時更新它。
    placeholder_caption = st.sidebar.empty()
    
    # 3. 定義回調函數
    def update_message():
        with st.spinner(f"載入最新熱門股票清單..."):
            hot_df = merge_and_save_hot_stocks(limit=limit)
            success_placeholder.success(f"✅ 已更新熱門股（共 {limit} 筆）")
            time.sleep(3)
            success_placeholder.empty()
            
        st.session_state.counter += 1
        # 使用傳入的 prefix_text 參數
        st.session_state.caption_message = f"📅 熱門股更新至：{hot_df['UpdateTime'][0]}"
    
    # 4. 使用佔位符來顯示 caption 訊息
    # 每次腳本重新執行時，佔位符都會用 session_state 中的最新值來更新
    placeholder_caption.caption(st.session_state.caption_message)
    
    st.sidebar.button("更新熱門股清單", on_click = lambda: update_message())
    
    success_placeholder = st.sidebar.empty()
    
def render_performance_metrics(stock_data_df: pd.DataFrame, stock_name: str):
    
    st.subheader(f"🔔 {stock_name} 績效與風險統計")
    
    # 取得收盤價序列
    prices = stock_data_df['close_price']
    
    # 計算日報酬率
    returns = prices.pct_change().dropna()

    # --- 1. 計算所有指標 ---
    try:
        ann_return = calculate_annualized_return(returns)
        max_drawdown = calculate_max_drawdown(prices)
        volatility = calculate_annualized_volatility(returns)
        
        # 為了計算夏普比率，假設無風險利率為 2% (0.02)
        risk_free_rate = 0.02
        sharpe_ratio = (ann_return - risk_free_rate) / volatility if volatility != 0 else 0

    except Exception as e:
        st.error(f"計算績效指標時發生錯誤: {e}")
        return

    # --- 2. 視覺化：數值摘要卡片 ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("年化報酬率", f"{ann_return:.2%}", help="代表資產每年平均回報")
    with col2:
        # 最大回撤通常為負值，但顯示時習慣用正值
        st.metric("最大回撤 (MDD)", f"{abs(max_drawdown):.2%}", help="從高點到低點的最大跌幅")
    with col3:
        st.metric("年化波動率", f"{volatility:.2%}", help="衡量價格波動風險")
    with col4:
        st.metric("夏普比率", f"{sharpe_ratio:.2f}", help="每承擔一單位風險所獲得的超額報酬")

    st.markdown("---")
    
    # --- 3. 視覺化：累積報酬率圖表 ---
    st.subheader(f"🔔 {stock_name} 累積報酬與回撤趨勢")
    fig = plot_cumulative_returns_and_drawdown(prices, stock_name)
    st.plotly_chart(fig, use_container_width=True)

    
    
    
if __name__ == "__main__":
    run_dashboard()       
     