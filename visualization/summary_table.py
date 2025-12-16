"""
visualization/summary_table.py
----------------
建立多股票技術指標摘要表格。
整合各股票分析結果供 dashboard 顯示。
"""

from utils.helpers import setup_logger
import streamlit as st
import pandas as pd
from analytics.portfolio_stats import (
    generate_summary_table, 
    export_summary_to_excel
)

logger = setup_logger("summary_table")

def build_summary_table(stock_data_dict: dict) -> pd.DataFrame:
    """
    建立多股票技術指標摘要表格並匯出檔案
    
    參數：
        stock_data_dict (dict): 股價資料
    
    返回型別：
        pd.Dataframe
    """
    df_summary = generate_summary_table(stock_data_dict)
    st.dataframe(
        df_summary["summary"].style.highlight_max(
            subset=["收盤價", "漲跌幅(%)", "RSI", "MACD"], color="#c1e1c1"
        ).highlight_min(
            subset=["RSI", "MACD"], color="#f4cccc"
        ),
        use_container_width=True
    )           
    st.dataframe(
        df_summary["performance"].style.highlight_max(
            subset=["年化報酬率"], color="#c1e1c1"
        ).highlight_min(
            subset=["波動率", "最大回撤"], color="#f4cccc"
        ),
        use_container_width=False
    )            

    # 下載報表功能
    st.markdown("### 📥 匯出報表")
    excel_data = export_summary_to_excel(df_summary)
    st.download_button(
        label="下載 Excel 摘要表",
        data=excel_data,
        file_name="stock_analytics.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def render_performance_ranking_table(ranking_df: pd.DataFrame, title: str = ""):
    """
    將股票報酬率排行榜數據呈現為 Streamlit 表格。
    
    Args:
        ranking_df: 包含 stock_id 和 total_return 的數據框。
        title: 表格標題。
    """
    st.markdown(title)
    
    # 格式化顯示 (報酬率顯示為百分比)
    display_df = ranking_df.copy()
    display_df['總報酬率'] = (display_df['total_return'] * 100).map('{:.2f}%'.format)
    
    # 重新命名欄位以便於閱讀
    display_df.rename(columns={
        'stock_id': '股票代碼',
        'industry': '產業別',
        'start_price': '區間期初價',
        'end_price': '區間期末價',
    }, inplace=True)
    
    # 選擇最終要呈現的欄位
    final_cols = ['股票代碼', '區間期初價', '區間期末價', '總報酬率']
    
    # 使用 Streamlit 顯示表格
    st.dataframe(
        display_df[final_cols],
        hide_index=True,
        use_container_width=True
    )
    
def render_generic_ranking_table(
    ranking_df: pd.DataFrame, 
    title: str, 
    metric_name: str,
    key_col: str = 'stock_id',        # 新增: 作為主要識別碼的欄位 (e.g., '代碼', '產業名稱')
    metric_col: str = '排序指標值',   # 新增: 包含要格式化的數值的欄位
    display_cols: list = None         # 新增: 最終要顯示的欄位列表
):
    """
    將通用的排行榜數據呈現為 Streamlit 表格，並根據指標名稱自動格式化數值。

    Args:
        ranking_df: 包含所有必要欄位的 DataFrame。
        title: 表格標題 (通常是指標名稱)。
        metric_name: 指標的中文名稱 ("百分比", "成交量", "股價")，決定格式化方式。
        key_col: 作為主要識別碼的欄位名稱。
        metric_col: 包含數值指標的欄位名稱。
        display_cols: 最終要在表格中呈現的欄位順序。
    """
    if ranking_df.empty:
        st.info(f"無 {title} 數據可供顯示。")
        return

    st.markdown(title)
    
    display_df = ranking_df.copy()
    
    # 1. 數值格式化
    if metric_col in display_df.columns:
        # 根據 metric_name 決定格式化方式
        if metric_name in ["百分比", "漲跌幅", "累積報酬率"]:
            # 適用於 daily_return, cumulative_return, average_daily_return (必須是小數)
            display_df[metric_col] = (display_df[metric_col] * 100).map('{:.2f}%'.format)
        
        elif metric_name in ["成交量", "總成交量", "股數"]:
            # 適用於 volume, total_volume, foreign_net_shares (大整數)
            # 使用千位分隔符
            display_df[metric_col] = display_df[metric_col].map('{:,.0f}'.format)
        
        elif metric_name in ["金額", "股價"]:
            # 適用於 close_price 或其他貨幣/金額
            display_df[metric_col] = display_df[metric_col].map('NT${:,.2f}'.format)
    
    # 2. 準備顯示欄位
    
    # 如果未指定 display_cols，則默認顯示所有欄位 (但通常建議明確指定)
    if display_cols is None:
        final_cols = display_df.columns.tolist()
    else:
        # 確保指定的欄位都在 DataFrame 中
        final_cols = [col for col in display_cols if col in display_df.columns]
        
    # 3. 呈現表格
    st.dataframe(
        display_df[final_cols],
        hide_index=True,
        use_container_width=True
    )