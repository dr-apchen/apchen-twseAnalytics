"""
visualization/dashboard.py
-------------
Streamlit 主介面。
整合 data_updater 自動補抓功能，確保使用者查詢期間資料完整。
"""
from utils.helpers import setup_logger
import streamlit as st
import pandas as pd
from datetime import (
    datetime,
    timedelta
)
from analytics.trend_analysis import analyze_trend
from analytics.indicators import calculate_all_indicators
from utils.stock_info_map import get_stock_name
from visualization.summary_table import build_summary_table
from visualization.chart_utils import (
    plot_price_ma,
    plot_rsi,
    plot_macd,
    plot_bollinger_bands,
    plot_volume
)

from data_collector.data_updater import fetch_and_store, check_stock_data_exists, load_stock_data

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
        st.error("❌ 抓取 {stock_id} 資料失敗，請檢查股票代碼或網路連線")
        
    # Step 3: 偵測資料庫缺口
    else:
        latest_date_in_db = df["trade_date"].max().date()
    
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
    st.title("📈 動態股市分析平台")
    
    # 取得使用者模式選擇
    st.sidebar.header("🔍 功能選單")
    mode = st.sidebar.radio("選擇分析模式：", ["個股分析", "多股票摘要表"])
    # 共用日期範圍    
    st.sidebar.subheader("📆 日期設定")
    start_date = st.sidebar.date_input("開始日期", datetime(2023, 1, 1))
    end_date = st.sidebar.date_input("結束日期", datetime.today() - timedelta(days=1))
    
    # ================================
    # 模式一：個股分析
    # ================================
    if mode == "個股分析":
        st.sidebar.subheader("📊 輸入股票代號")
        stock_id = st.sidebar.text_input("請輸入股票代號（例如：2330）")

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
    st.sidebar.markdown("**版本**：Beta 1.0")
            
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
    
if __name__ == "__main__":
    run_dashboard()       
     