"""
setup_env.py
-------
環境初始化檢查與自動安裝腳本
此腳本會：
1. 檢查並安裝必要套件
2. 測試 MySQL 連線是否正常
3. 測試 yfinance 是否可用
"""

import importlib
import subprocess
import sys

REQUIRED_PACKAGES = [
    "yfinance",
    "pandas",
    "selenium",
    "mysql-connector-python",
    "schedule",
    "streamlit",
    "plotly",
    "pdoc"
]

def install_package(package):
    """安裝指定套件"""
    try:
        print(f"📦 安裝套件：{package} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        print(f"❌ 套件安裝失敗：{package} - {e}")

def check_and_install_packages():
    """檢查每個套件是否存在，若無則安裝"""
    print("🔍 開始檢查環境套件...")
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package.split("==")[0])
            print(f"✅ {package} 已安裝")
        except ImportError:
            install_package(package)
    print("✅ 所有必要套件已準備完成\n")

def test_yfinance():
    """測試 yfinance 抓取功能"""
    try:
        import yfinance as yf
        print("🚀 測試 yfinance 下載台積電資料...")
        ticker = yf.Ticker("2330.TW")
        df = ticker.history(period="5d")
        if not df.empty:
            print("✅ yfinance 運作正常，成功抓到資料！")
        else:
            print("⚠️ yfinance 無法取得資料，請檢查網路或股票代碼。")
    except Exception as e:
        print("❌ yfinance 測試失敗：", e)

def test_mysql_connection():
    """測試 MySQL 連線"""
    try:
        from database.db_connection import get_connection, close_connection
        conn = get_connection()
        if conn:
            print("✅ MySQL 連線測試成功")
            close_connection(conn)
        else:
            print("⚠️ MySQL 連線失敗，請確認 db_config.py 設定")
    except Exception as e:
        print("❌ 測試 MySQL 連線失敗：", e)

if __name__ == "__main__":
    print("🚧 初始化環境開始...\n")
    check_and_install_packages()
    test_yfinance()
    test_mysql_connection()
    print("\n🎉 環境檢查完成！你可以執行： python main.py")
