"""
data_collector/scheduler.py
---------------
每日自動排程抓取股價資料
使用 schedule 套件
"""
from utils.helpers import setup_logger
import schedule
import time
from data_collector.data_updater import update_all_stocks
from data_collector.institutional_investor_fetcher import InstitutionalFetcher
logger = setup_logger("scheduler")

def job():
    """
    執行更新作業
    
    參數：
        NA
    
    返回：
        NA
    """
    
    print("⏰ 開始獲取三大法人最新資料...")
    fetcher = InstitutionalFetcher()
    institutional_data = fetcher.run_update() #datetime.date(2025, 12, 12)
    print("✅ 三大法人資料更新完成")
    
    print("⏰ 開始自動抓取每日股價資料...")
    # run through existing listed stocks in stock_info and fetch the latest data
    update_all_stocks()
    print("✅ 每日股價資料更新完成")
    
    return

def run_scheduler(t: str):
    """
    批次執行更新作業設定
    
    參數：
        NA
    
    返回：
        NA
    """
    
    schedule.every().day.at(t).do(job)
    print(f"🕘 排程啟動，等待每日 {t} 自動抓取...")

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分鐘檢查一次
