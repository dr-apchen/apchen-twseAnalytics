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
from analytics.industry_analysis import IndustryAnalyzer
from utils.stock_info_map import get_stock_name, get_all_industry, get_stock_ids_by_industry
from visualization.summary_table import build_summary_table, render_performance_ranking_table
from visualization.chart_utils import (
    plot_price_ma,
    plot_rsi,
    plot_macd,
    plot_bollinger_bands,
    plot_volume,
    plot_industry_cumulative_return
)
from data_collector.data_updater import (
    fetch_and_store,
    check_stock_data_exists,
    load_stock_data,
    check_stock_data_uptodate
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

def ensure_data_completeness(stock_id: str, start_date: str, end_date: str, flag: bool = False):
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
    with st.spinner(f"📥 確認資料庫中股票代碼 {stock_id} 資料是否完整..."):
        exists = check_stock_data_exists(stock_id, start_date, end_date)
    if not exists:
        print(f"⚠️ 資料庫中無 {stock_id} 資料，自動抓取中...")
        with st.spinner(f"📥 資料庫中無 {stock_id} 資料，自動抓取中..."):
            updates = fetch_and_store(stock_id, start_date, end_date)

        # schedule.every().day.at("09:00").do(daily_task, stock_id=stock_id)
        # print(f"⏰ 已設定每日 9:00 自動抓取 {stock_id} 資料並更新技術指標")

    # Step 2: 讀取資料庫
    with st.spinner(f"⏳ 載入資料庫中 {stock_id} 資料..."):
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
            # placeholder = st.empty()
            with st.spinner(f"📥 確認 {stock_id} (股票代碼) {missing_start} 到 {end_date} 期間資料..."):
                updates = fetch_and_store(stock_id, missing_start, end_date)
                df = load_stock_data(stock_id, start_date, end_date)
                # if(updates is True):
                #     placeholder.success(f"✅ {stock_id} 資料已更新")
                # else:
                #     placeholder.success(f"✅ {stock_id} 資料無更新")
                # if(flag == True):
                #     placeholder.empty()
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
    mode = st.sidebar.radio("選擇分析模式：", ["個股分析", "多股票摘要表", "產業分析"])        
    # 共用日期範圍    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.sidebar.date_input("📆 開始日期", datetime(2023, 1, 1))
    with col2:    
        end_date = st.sidebar.date_input("📆 結束日期", datetime.today() - timedelta(days=2))
        
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
        stock_uptodate = check_stock_data_uptodate(stock_ids, start_date, end_date)
        for index, stock_id in enumerate(stock_ids):
            stock_name = get_stock_name(stock_id)
            if(stock_id in stock_uptodate):
                with st.spinner(f"⏳ 載入資料庫中 {stock_id} 資料..."):
                    df = load_stock_data(stock_id, start_date, end_date)
            else:
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
    # ================================
    # 模式三：產業分析頁面
    # ================================
    elif mode == "產業分析":
        st.subheader("🏭 單一產業別市場分析")       
        
        # --- 1. 使用者輸入選單 ---
        # 假設 get_all_industry_names() 從 DB 讀取所有產業名稱
        all_industries = get_all_industry()
        if "nan" in all_industries:
            all_industries.remove("nan")
        if len(all_industries) < 1:
            st.error("❌ 無法取得產業別清單，請重新開啟頁面以確保台股產業資料已下載。")
        else:
            selected_industry = st.sidebar.selectbox(
                "選擇產業別", [""] + [f"{i}" for i in all_industries]
            )
        
            if selected_industry:
                # --- 2. 數據載入與分析 ---
                with st.spinner(f"📥 正在載入 {selected_industry} 的數據並進行分析..."):
                    print(f"🔄 更新中: {selected_industry}")
                    # A. 載入數據 (呼叫 data_loader)
                    
                    stock_ids = get_stock_ids_by_industry(selected_industry)
                    stock_id_len = len(stock_ids)
                    if not stock_ids:
                        st.info("💡 請在左側選取一個產業別。")
                        return
                    
                with st.spinner(f"📥 正在載入 {stock_id_len} 筆股票數據並進行分析..."):
                    status_text = st.empty()
                    percent_complete = 0
                    my_progress_bar = st.progress(percent_complete, text="⏳ 資料載入中，請稍候...")
                    percent_interval = 1/stock_id_len
                    industry_stock_data = pd.DataFrame()
                    stock_uptodate = check_stock_data_uptodate(stock_ids, start_date, end_date)
                    for index, stock_id in enumerate(stock_ids):
                        stock_name = get_stock_name(stock_id)
                        if(stock_id in stock_uptodate):
                            with st.spinner(f"⏳ 載入資料庫中 {stock_id} 資料..."):
                                df = load_stock_data(stock_id, start_date, end_date)
                        else:
                            df = ensure_data_completeness(stock_id, start_date, end_date)
                        # df = ensure_data_completeness(stock_id, start_date, end_date)
                        if df.empty:
                            return
                        
                        if not df.empty:
                            df["stock_name"] = stock_name
                            df["industry"] = selected_industry
                            industry_stock_data = pd.concat([industry_stock_data, df], ignore_index=True)
                        percent_complete += percent_interval 
                        my_progress_bar.progress(percent_complete, text=f"⏳ 資料載入中，進度 {(percent_complete*100):.0f}%...")
            
                    # status_text.text("🎉 產業別股價資料載入完成。")
                    my_progress_bar.empty()
                    
                    if industry_stock_data.empty:
                        st.error(f"❌ 在所選區間內，找不到 {selected_industry} 的股價數據。")
                        return
                    else: 
                        # B. 進行分析 (呼叫 IndustryAnalyzer)
                        data_with_returns = IndustryAnalyzer.calculate_industry_stock_returns(pd.DataFrame(industry_stock_data))
                        industry_daily_perf = IndustryAnalyzer.aggregate_industry_performance(data_with_returns)
                        stock_ranking_df = IndustryAnalyzer.calculate_stock_total_returns(industry_stock_data) 
                        # C. 【新增】計算個股總報酬率
                        stock_ranking_df = IndustryAnalyzer.calculate_stock_total_returns(industry_stock_data)
                        # --- 3. 結果視覺化 ---
                        st.markdown(f"📊 {selected_industry} 趨勢分析")
                        
                        # 繪製產業累積報酬率圖
                        if data_with_returns.empty or industry_daily_perf.empty:
                            st.error(f"❌ 無法計算 {selected_industry} 趨勢分析")
                        else: 
                            fig_cum_ret = plot_industry_cumulative_return(
                                data_with_returns, 
                                industry_daily_perf, 
                                stock_ranking_df, # 排行榜數據
                                n_highlight=5     # 可調整突顯的數量
                            )
                            st.plotly_chart(fig_cum_ret, use_container_width=True)
                        st.markdown("---")
        
                        # 顯示個股報酬率排行榜 (呼叫 summary_table 模組)
                        if not stock_ranking_df.empty:
                            render_performance_ranking_table(
                                stock_ranking_df,
                                title=f"📈 {selected_industry} 產業內個股區間總報酬率排行榜({start_date} ~ {end_date})"
                            )
                        else:
                            st.info("該區間內無有效的個股報酬率數據。")
            else:
                st.info("💡 請在左側選取一個產業別。")
                
            
    st.sidebar.markdown("---")
    st.sidebar.markdown("**版本**： Beta 1.1")
            
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
     