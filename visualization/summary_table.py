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
    """TODO: Add docstring for def build_summary_table(stock_data_dict: dict) -> pd.DataFrame:"""
    df_summary = generate_summary_table(stock_data_dict)
    st.dataframe(
        df_summary.style.highlight_max(
            subset=["收盤價", "漲跌幅(%)", "RSI", "MACD"], color="#c1e1c1"
        ).highlight_min(
            subset=["RSI", "MACD"], color="#f4cccc"
        ),
        use_container_width=True
    )                    

    # 下載報表功能
    st.markdown("### 📥 匯出報表")
    excel_data = export_summary_to_excel(df_summary)
    st.download_button(
        label="下載 Excel 摘要表",
        data=excel_data,
        file_name="stock_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
