# 動態股市趨勢分析小精靈 (台股上市上櫃)

verson: 1.0

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
### 簡報介紹
<br/>
1. Beta 1.0
<a href="https://reurl.cc/xKEkm5" target="_blank">
<img width="250" height="250" alt="qrcode" src="https://github.com/user-attachments/assets/2c04e7ca-ab46-4be4-b7ec-14dd5b9cbdf6" />
</a>
