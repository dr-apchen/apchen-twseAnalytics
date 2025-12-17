"""
utils/helpers.py
-----------
提供常用工具：日誌設定、日期區間產生等。
"""

import os
import logging
# from datetime import datetime, timedelta

def setup_logger(name="app", level=logging.INFO):
    """
    建立統一日誌紀錄器
    
    參數：
        name (str): 預設名稱
        level (int): 預設類型
    
    返回：
        logging.getLogger(name)
    """
    os.makedirs("data/logs", exist_ok=True)
    log_path = os.path.join("data/logs", f"{name}.log")

    logging.basicConfig(
        filename=log_path,
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        encoding="utf-8"
    )
    return logging.getLogger(name)

# def date_range(start_date, end_date):
#     """產生日期範圍清單 (YYYY-MM-DD 格式)"""
#     start = datetime.strptime(str(start_date), "%Y-%m-%d")
#     end = datetime.strptime(str(end_date), "%Y-%m-%d")
#     days = []
#     while start <= end:
#         days.append(start.strftime("%Y-%m-%d"))
#         start += timedelta(days=1)
#     return days
