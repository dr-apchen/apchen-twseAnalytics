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