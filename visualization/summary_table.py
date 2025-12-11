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
