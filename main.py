"""
./main.py
-------
主入口：檢查股票清單、確保資料更新，啟動 Dashboard。
"""

from utils.helpers import setup_logger
import sys
from datetime import datetime
import subprocess
import schedule
import time
from visualization.dashboard import ensure_data_completeness

logger = setup_logger("main")

def main():
    """TODO: Add docstring for def main():"""
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "dashboard"

    if cmd == "fetch":
        stock_id = input("請輸入股票代號: ").strip()
        start_date = input("請輸入開始日期 (YYYY-MM-DD): ").strip()
        end_date = input("請輸入結束日期 (YYYY-MM-DD): ").strip()
        ensure_data_completeness(stock_id, start_date, end_date)

    elif cmd == "dashboard":
        open_dashboard()

        # while True:
        #     schedule.run_pending()
        #     time.sleep(30)
    else:
        print("未知參數，請使用 fetch 或 dashboard")
        
# ---------------------
# 啟動 Dashboard
# ---------------------
def open_dashboard():
    """TODO: Add docstring for def open_dashboard():"""
    print("🌐 啟動 Dashboard...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "visualization/dashboard.py"])

# ---------------------
# 每日排程
# ---------------------
def daily_task(stock_id: str):
    """TODO: Add docstring for def daily_task(stock_id: str):"""
    yesterday = (datetime.today()).strftime("%Y-%m-%d")
    ensure_data_completeness(stock_id, start_date=yesterday, end_date=yesterday)

# ---------------------
# 主程式
# ---------------------
if __name__ == "__main__":
    main()

