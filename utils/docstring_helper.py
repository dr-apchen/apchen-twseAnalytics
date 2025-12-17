"""
utils/docstring_helper.py

模組用途：
    自動檢查與補齊專案中缺少的 docstring，以維持程式碼文件品質。

使用方式：
    python -m utils.docstring_helper --auto
"""
import ast
import os
import argparse

def check_and_add_docstrings(root_path=".", auto_add=False):
    """
    掃描專案並檢查缺少的 docstring，必要時自動補齊。

    Args:
        root_path (str): 專案根目錄。
        auto_add (bool): 若為 True，會在缺少 docstring 的函式自動加上模板。
    """
    for dirpath, _, filenames in os.walk(root_path):
        for file in filenames:
            if file.endswith(".py") and "venv" not in dirpath and "docs" not in dirpath:
                file_path = os.path.join(dirpath, file)
                process_file(file_path, auto_add)

def process_file(file_path, auto_add):
    """
    檢查單一檔案中的所有類別與函式，找出缺少 docstring 的項目。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        print(f"⚠️ 跳過無法解析的檔案: {file_path}")
        return

    missing_items = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            docstring = ast.get_docstring(node)
            if not docstring:
                missing_items.append(node.name if hasattr(node, "name") else "module")

    if missing_items:
        print(f"\n📄 {file_path}")
        for name in missing_items:
            print(f"  ⚠️ 缺少 docstring → {name}")
        if auto_add:
            add_placeholder_docstring(file_path, missing_items)

def add_placeholder_docstring(file_path, missing_items):
    """
    自動為缺少 docstring 的函式/類別新增模板。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        new_lines.append(line)
        if any(f"def {name}(" in line or f"class {name}" in line for name in missing_items):
            indent = " " * (len(line) - len(line.lstrip()) + 4)
            new_lines.append(f'{indent}"""TODO: Add docstring for {line.strip()}"""\n')

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"✅ 已自動補齊 docstring 模板：{file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="掃描並補齊專案 docstring")
    parser.add_argument("--path", type=str, default=".", help="專案根目錄路徑")
    parser.add_argument("--auto", action="store_true", help="自動補齊缺少的 docstring")
    args = parser.parse_args()

    check_and_add_docstrings(args.path, args.auto)
