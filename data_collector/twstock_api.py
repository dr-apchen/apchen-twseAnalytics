"""
data_collector/twstock_api.py
---------------
使用 twstock 套件取得股票資料
"""

from utils.helpers import setup_logger
import twstock #pip install --user twstock
from twstock import Stock
from twstock import BestFourPoint
import pandas as pd
from datetime import datetime

logger = setup_logger("twstock_api")

stockData = {}

def fetch_stock_data(stock_code):
    """
    抓取TWSE股票歷史資料
    
    參數：
        stock_code (str): 股票代碼
    
    返回：
        NA
    """

    if type(stock_code) is str:
        print(stock_code)
        stock = Stock(stock_code)                         # 擷取台積電股價
        stock.fetch_from(2024, 1)
        stockData = stock.price
        # ma_p = stock.moving_average(stock.price, 5)       # 計算五日均價
        # ma_c = stock.moving_average(stock.capacity, 5)    # 計算五日均量
        # ma_p_cont = stock.continuous(ma_p)                # 計算五日均價持續天數
        # ma_br = stock.ma_bias_ratio(5, 10)                # 計算五日、十日乖離值
        # bfp = BestFourPoint(stock)
        # bfp.best_four_point_to_buy()    # 判斷是否為四大買點
        # bfp.best_four_point_to_sell()   # 判斷是否為四大賣點
        # bfp.best_four_point()           # 綜合判斷
        # stock = twstock.realtime.get(stock_code)    # 擷取當前台積電股票資訊
    
    elif type(stock_code) is list:
        print(stock_code)
        stock = twstock.realtime.get(stock_code)  # 擷取當前三檔資訊

    if not stock:
        print("no data")
    else:
        now = datetime.now()
        formatted_string = now.strftime("_%y%m%d-%H%M%S")
        print(stockData)
        # df = pd.DataFrame(stock)
        # df.to_csv("data/twstock_data"+formatted_string+".csv", index=False, encoding="utf-8-sig")
    
def fetch_stock_name(stock_code: str) -> str:
    """
    抓取TWSE股票資料
    
    參數：
        stock_code (str): 股票代碼
    
    返回：
        NA
    """

    # print(twstock.codes)                # 列印台股全部證券編碼資料
    print(twstock.codes[stock_code])        # 列印 2330 證券編碼資料
    # twstock.StockCodeInfo(type='股票', code='2330', name='台積電', ISIN='TW0002330008', start='1994/09/05', market='上市', group='半導體業', CFI='ESVUFR')
    # print(twstock.codes['2330'].name)   # 列印 2330 證券名稱
    # '台積電'
    # print(twstock.codes['2330'].start)  # 列印 2330 證券上市日期
    # '1994/09/05'
    
    
fetch_stock_data('2330')
# fetch_stock_data(['2330', '2337', '2409'])
# fetch_stock_name('2330')