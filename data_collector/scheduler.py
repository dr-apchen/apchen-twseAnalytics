"""
data_collector/scheduler.py
---------------
每日自動排程抓取股價資料
使用 schedule 套件
"""

from utils.helpers import setup_logger
import schedule
import time
from visualization.dashboard import fetch_and_store
# from data_collector.twse_crawler import fetch_twse_stock_list

logger = setup_logger("scheduler")

def job():
    """TODO: Add docstring for def job():"""
    print("⏰ 開始自動抓取每日股價資料...")
    fetch_and_store()
    print("✅ 每日股價資料更新完成")

def run_scheduler():
    """TODO: Add docstring for def run_scheduler():"""
    # schedule.every().day.at("04:30").do(fetch_twse_stock_list)
    # 設定每天上午 9:30 自動執行（台股開盤前）
    schedule.every().day.at("09:30").do(job)
    print("🕘 排程啟動，等待每日自動抓取...")

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分鐘檢查一次
