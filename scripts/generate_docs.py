"""
scripts/generate_docs.py
相容最新版 pdoc (v13+)
✨ 新增功能：
1. 自動開啟瀏覽器顯示 docs/index.html
2. 生成過程與錯誤記錄到 scripts/logs/docgen.log

執行: python scripts/generate_docs.py --ignore-errors --open

"""

import os
import sys
import subprocess
import argparse
import types
import shutil
import datetime
import webbrowser

# -----------------------------
# 工具函式
# -----------------------------
def log(message, log_file="scripts/logs/docgen.log"):
    """寫入日誌文件"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def safe_imports(mock_modules=None):
    """建立假的模組以防止 import 錯誤。"""
    if mock_modules is None:
        mock_modules = [
            "mysql", "mysql.connector", "yfinance", "streamlit",
            "pandas", "plotly", "schedule", "requests", "matplotlib", "dash"
        ]
    for mod in mock_modules:
        if mod not in sys.modules:
            sys.modules[mod] = types.ModuleType(mod)

def discover_modules(project_root):
    """找出專案中所有可供 pdoc 文件化的模組或套件。"""
    modules = []
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), project_root)
                module = rel_path.replace(os.sep, ".")[:-3]  # 轉為模組格式
                if not module.startswith("scripts."):  # 排除 scripts 內的檔案
                    modules.append(module)
    return modules

# -----------------------------
# 主流程
# -----------------------------
def run_pdoc(output_dir="docs", ignore_errors=False, open_browser=False):
    """執行 pdoc 生成文件。"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    log(f"📂 已切換至專案根目錄：{project_root}")

    if ignore_errors:
        safe_imports()
        log("🧩 已啟用 safe_imports 模式（忽略 import 錯誤）")

    modules = discover_modules(project_root)
    if not modules:
        msg = "❌ 未找到任何可生成文件的 Python 模組。"
        log(msg)
        raise ValueError(msg)

    log(f"🧠 發現 {len(modules)} 個模組待生成：")
    for m in modules:
        log(f"   - {m}")

    if shutil.which("pdoc"):
        cmd = ["pdoc", "--output-dir", output_dir] + modules
    else:
        cmd = [sys.executable, "-m", "pdoc", "--output-dir", output_dir] + modules

    log(f"🚀 執行命令: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        abs_path = os.path.abspath(output_dir)
        log(f"✅ 文件已生成：{abs_path}")

        index_file = os.path.join(abs_path, "index.html")
        if open_browser and os.path.exists(index_file):
            webbrowser.open_new_tab(f"file://{index_file}")
            log(f"🌐 已自動開啟瀏覽器：{index_file}")
        elif not os.path.exists(index_file):
            log("⚠️ 找不到 index.html，請確認 pdoc 是否成功輸出。")

    except subprocess.CalledProcessError as e:
        log(f"❌ 生成文件失敗: {e}")
        sys.exit(1)
    except FileNotFoundError:
        log("❌ 找不到 pdoc，請先安裝：pip install -U pdoc")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate documentation using pdoc (v13+).")
    parser.add_argument("--output", "-o", type=str, default="docs", help="輸出資料夾 (預設: docs)")
    parser.add_argument("--ignore-errors", "-i", action="store_true", help="忽略 import 錯誤，自動 mock 外部模組")
    parser.add_argument("--open", "-b", action="store_true", help="生成後自動開啟瀏覽器預覽")
    args = parser.parse_args()

    run_pdoc(output_dir=args.output, ignore_errors=args.ignore_errors, open_browser=args.open)

if __name__ == "__main__":
    main()
