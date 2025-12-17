"""
./main.py
-------
主入口：檢查股票清單、確保資料更新，啟動 Dashboard。
"""

from utils.helpers import setup_logger
import sys
import subprocess
from visualization.dashboard import ensure_data_completeness
from database.db_connection import get_connection, close_connection
from data_collector.scheduler import run_scheduler

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
        conn = get_connection()
        stock_id = input("請輸入股票代號: ").strip()
        start_date = input("請輸入開始日期 (YYYY-MM-DD): ").strip()
        end_date = input("請輸入結束日期 (YYYY-MM-DD): ").strip()
        ensure_data_completeness(conn, stock_id, start_date, end_date)
        close_connection(conn)
    elif cmd == "dashboard":
        open_dashboard()
        
    elif cmd == "daily":
        t = sys.argv[2].lower() if len(sys.argv) > 2 else "09:30"
        daily_task(t)
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
def daily_task(t: str):
    """
    每日排程
    
    參數：
        NA
    
    返回：
        NA
    """
    run_scheduler(t)
    

# ---------------------
# 主程式
# ---------------------
if __name__ == "__main__":
    main()
    

