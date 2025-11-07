"""
test_data_loader.py
-------------------
基礎資料庫測試：確認 MySQL 連線成功。
"""

import unittest
from database.db_connection import get_connection

class TestDatabase(unittest.TestCase):
    """TODO: Add docstring for class TestDatabase(unittest.TestCase):"""
    def test_connection(self):
        """TODO: Add docstring for def test_connection(self):"""
        conn = get_connection()
        self.assertIsNotNone(conn)
        conn.close()

if __name__ == "__main__":
    unittest.main()
