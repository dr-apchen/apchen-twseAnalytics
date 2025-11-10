"""
./main.py
-------
主入口：檢查股票清單、確保資料更新，啟動 Dashboard。
"""

from utils.helpers import setup_logger
import sys
import subprocess
from visualization.dashboard import ensure_data_completeness
from datacollector.scheduler import run_scheduler

logger = setup_logger("main")

def main():
    """
    分為fetch/dashboard模式，預設為dashboard模式開始主頁面
    
    參數： 
        NA
    
    返回：
        NA
    """
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
    """
    啟動 Dashboard
    
    參數：
        NA
    
    返回：
        NA
    """
    print("🌐 啟動 Dashboard...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "visualization/dashboard.py"])

# ---------------------
# 每日排程
# ---------------------
def daily_task():
    """
    每日排程
    
    參數：
        NA
    
    返回：
        NA
    """
    run_scheduler()
    

# ---------------------
# 主程式
# ---------------------
if __name__ == "__main__":
    main()

