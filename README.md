# 動態股市趨勢分析小精靈 (台股上市上櫃) verson: 1.1

### 初始化環境
1. 安裝MySQL
2. 進入 *[db_config.py](https://github.com/dr-apchen/apchen-twseAnalytics/blob/main/database/db_config.py)* 修改資料庫連線設定
3. 開啟 MSQL 輸入 *[table.sql](https://github.com/dr-apchen/apchen-twseAnalytics/blob/main/database/table.sql)* 所提供指令建立資料表
4. 執行程式
   ```
   python setup_env.py  --初始化環境
   ```
5. 確認環境測試通過後執行主程式
   ```
   python main.py  --啟動專案
   ```
***
### 手動安裝專案環境
如套件發生問題，可透過手動方式安裝環境需求套件。
```
pip install -r requirements.txt
```
***
### 執行模式
1. dashboard: 網頁介面 (預設開啟，"dashboard" 可省略)
```
pip main.py dashboard
```
2. fetch: 手動獲取股價資料
```
pip main.py fecth
```
3. daily: 每日排程自動更新資料 (daily 後方時間可選填，不填為預設 09:30)
```
pip main.py daily 14:30
```
***
### 專案架構
##### 參考  *[Docstring File](https://htmlpreview.github.io/?https://github.com/dr-apchen/apchen-twseAnalytics/blob/main/docs/index.html)*
```
twseAnalytics/
│
├── data_collector/                        # 資料蒐集層：外部資料來源 (API / 爬蟲 / 更新)
│   ├── yahoo_api.py                       ← yfinance 抓資料
│   ├── twse_crawler.py                    ← 爬取台股名稱、產業類別
│   ├── data_updater.py                    ← 自動巡檢、補抓資料
│   ├── scheduler.py                       ← 定時排程每日更新（若有）
│   ├── hot_stock_fetcher.py               ← 爬取台股熱門股資料
│   └── institutional_investor_fetcher.py  ← 爬取三大法人投資數據
│
├── database/                              # 資料層：與 MySQL 溝通
│   ├── db_config.py                       ← DB 連線設定
│   ├── db_connection.py                   ← 連線建立
│   ├── data_loader.py                     ← 讀寫資料庫、資料查詢封裝
│   └── stock_info_manager.py              ← 讀寫股票名稱、產業類別
│
├── analytics/                             # 分析層：技術指標與分析邏輯
│   ├── indicators.py                      ← 個股指標 (RSI, MACD, Bollinger, MA, Volume)
│   ├── trend_analysis.py                  ← 自動趨勢解讀（多頭/空頭訊號）
│   ├── portfolio_stats.py                 ← 多股票統計與報酬率、風險分析
│   ├── industry_analysis.py               ← 產業資料分析與排名
│   ├── investor_flow_analysis.py          ← 三大法人投資數據分析與排名
│   └── ranking_analyzer.py                ← 產業與個股漲跌幅排名
│
├── visualization/                         # 視覺化層：前端展示
│   ├── dashboard.py                       ← Streamlit 主頁
│   ├── chart_utils.py                     ← 繪圖工具（Plotly）
│   └── summary_table.py                   ← 多股票摘要表格
│
├── utils/                                 # 工具層：輔助模組
│   ├── stock_info_map.py                  ← 股票資訊對照
│   └── helpers.py                         ← 共用工具函式（ex: 日期處理、格式化）
│
├── data/                                  # 本地資料
│   ├── hot_stocks.csv                     ← 熱門股票清單
│   ├── tw_stock_list.csv                  ← 台股股票清單
│   ├── institutional_investor.csv         ← 三大法人買賣超清單
│   └── logs/                              ← 執行紀錄或錯誤日誌
│
├── tests/                                 # 單元測試
│   └── test_data_loader.py
│
└── main.py                                # 系統主入口：啟動更新 + Dashboard
```
***
### 功能分析
| 分類      | 模組                                            | 功能概要                   |
| :-------: | --------------------------------------------- | ---------------------- |
| 📥<br/>資料蒐集 | twse_crawler / yahoo_api / data_updater / <br/>hot_stock_fetcher / institutional_investor_fetcher     | 自動抓取台股清單、股價資料、<br/>熱門清單、補缺漏資料、<br/>抓取產業及法人    |
| 🧩<br/>資料庫  | db_config / db_connection / data_loader / <br/>stock_info_manager      | 管理 MySQL 存取與寫入         |
| 🕘<br/>排程  | scheduler      | 每日股價更新排程         |
| 📊<br/>分析   | indicators / trend_analysis / portfolio_stats / <br/>industry_analysis / investor_flow_analysis / <br/>ranking_analyzer| 技術指標計算、自動趨勢解讀、<br/>投資組合、產業、三大法人分析、<br/>排行榜統整   |
| 💡<br/>視覺化  | dashboard / chart_utils / summary_table       | 多股票圖表顯示、趨勢分析、<br/>股價趨勢摘要表、<br/>報酬率與風險摘要表      |
| 🧰<br/>工具   | stock_info_map / helpers                               | 股票資訊對照與更新、共用函式 |
| 🚀<br/>系統主控 | main                                       | 啟動流程、自動更新、<br/>執行 Dashboard |

***
### 開發計畫

1. 產業分析擴充

| 功能 | 價值評估 | 實作分析與視覺化 | 
| -- | -- | -- | 
| 產業平均漲跌幅 | 高價值。 這是判斷「今天哪個產業最熱/最冷」的核心指標，比單純的累積報酬率更具即時性。 | 1. 分析： 在 IndustryAnalyzer.aggregate_industry_performance 中，計算每日所有股票漲跌幅的平均值或加權平均值。 <br/>2. 視覺化： 繪製每日平均漲跌幅的長條圖 (Bar Chart)，正值用綠色，負值用紅色，易於辨識。 | 
| 產業平均成交量 | 中高價值。 衡量市場對該產業的關注程度和流動性。成交量放大通常是趨勢確認的信號。 | 1. 分析： 計算每日所有股票成交量的總和。 <br/>2. 視覺化： 繪製每日總成交量趨勢圖，通常搭配累積報酬率圖使用，作為輔助判斷。 | 
| 熱門產業 (產業漲跌幅排名) | 極高價值。 這是對上述數據的最終應用。使用者需要一個「市場儀表板」來快速查看哪個產業是當日焦點。 | 1. 分析： 新增一個 IndustryAnalyzer 或 RankingAnalyzer 函式，計算指定日期所有產業的平均漲跌幅，並按高到低排序。 <br/>2. 視覺化： 使用 表格或條形圖 呈現 Top 10 熱門（漲幅大）和 Bottom 10 冷門（跌幅大）產業。 | 

2. 交易策略模組 (strategies/)

預計更動結構:
```
twseAnalytics/
│
├── data_collector/                        # 資料蒐集層 (ETL)
│   ├── yahoo_api.py                       ← yfinance 抓取原始股價
│   ├── twse_crawler.py                    ← 爬取代碼、產業類別
│   ├── data_updater.py                    ← 自動巡檢、補抓資料
│   ├── scheduler.py                       ← 定時排程
│   ├── hot_stock_fetcher.py               ← 爬取熱門股資料
│   └── institutional_investor_fetcher.py  ← 爬取三大法人原始數據
│
├── database/                              # 資料儲存層 (MySQL)
│   ├── db_config.py                       ← DB 連線字串設定
│   ├── db_connection.py                   ← 連線建立
│   ├── data_loader.py                     ← 讀寫 stock_price_daily (更名後)
│   └── stock_info_manager.py              ← 讀寫股票資訊
│
├── analytics/                             # 分析運算層 (核心運算)
│   ├── indicators.py                      ← 技術指標計算 (RSI, MACD, Bollinger, MA)
│   ├── performance.py                     ← 【新增/重構】核心績效指標計算中心 (MDD, 年化報酬)
│   ├── trend_analysis.py                  ← 自動趨勢解讀 (調用 performance.py)
│   ├── industry_analysis.py               ← 產業排名與聚合 (Python/Pandas 計算)
│   ├── investor_flow_analysis.py          ← 法人數據分析
│   └── ranking_analyzer.py                ← 漲跌幅排名 (Python/Pandas 計算)
│
├── strategies/                            # 【新增】交易策略與回測層
│   ├── technical_strategies.py            ← 具體策略規則 (調用 indicators.py)
│   ├── backtester.py                      ← 回測執行引擎
│   └── evaluator.py                       ← 策略績效評估 (調用 performance.py)
│
├── visualization/                         # 視覺化展示層
│   ├── dashboard.py                       ← Streamlit 頁面控管與路徑
│   ├── chart_utils.py                     ← 通用繪圖工具 (K線、產業圖)
│   ├── strategy_plots.py                  ← 【新增】回測專用圖表 (淨值曲線、回撤圖)
│   └── summary_table.py                   ← 格式化表格 (支援中文對照與數值格式)
│
├── utils/                                 # 工具輔助層
│   ├── stock_info_map.py                  ← 股票資訊對照
│   └── helpers.py                         ← 日期處理、通用格式化
│
├── data/                                  # 本地暫存與日誌
│   ├── hot_stocks.csv
│   ├── tw_stock_list.csv
│   └── logs/
│
├── tests/                                 # 測試模組
│   ├── test_data_loader.py                ← 測試資料庫連線
│   └── test_performance.py                ← 測試報酬率與回撤計算準確性
│
└── main.py                                # 系統啟動入口
```
***
### 簡報介紹

Beta 1.0<br/>
<a href="https://reurl.cc/xKEkm5" target="_blank">
<img width="250" height="250" alt="qrcode" src="https://github.com/user-attachments/assets/2c04e7ca-ab46-4be4-b7ec-14dd5b9cbdf6" />
</a>
<br/><br/>
Beta 1.1<br/>
<a href="https://www.canva.com/design/DAG7K31aFJk/JXvx62JjBsSnUDTYXNkf9A/view?utm_content=DAG7K31aFJk&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h22da4afd3c" target="_blank">
<img width="250" height="250" alt="qrcode-canva-1 1" src="https://github.com/user-attachments/assets/00f0441a-7f76-40f5-b883-4dea16da09f1" />
</a>
<br/>
