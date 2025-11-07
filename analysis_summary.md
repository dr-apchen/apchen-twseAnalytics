# Uploaded Project Analysis: twseAnalytics.zip

Files analyzed and top-level functions/classes detected.

## twseAnalytics/analytics/indicators.py

- **Imports (sample):** `import pandas as pd`
- **Functions:** calculate_ma, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_volume_ma, calculate_all_indicators


## twseAnalytics/analytics/portfolio_stats.py

- **Imports (sample):** `import pandas as pd; from io import BytesIO
from analytics`
- **Functions:** generate_summary_table, export_summary_to_excel


## twseAnalytics/analytics/trend_analysis.py

- **Imports (sample):** `import pandas as pd; from database.db_connection import get_connection, close_connection
from analytics`
- **Functions:** load_stock_data, analyze_stock_trend, analyze_trend


## twseAnalytics/data_collector/data_updater.py

- **Imports (sample):** `from datetime import date, timedelta
from database; from data_collector.yahoo_api import fetch_and_store


def get_stock_latest_date`
- **Functions:** get_stock_latest_date, update_stock_if_needed, update_all_stocks


## twseAnalytics/data_collector/scheduler.py

- **Imports (sample):** `import schedule; import time; from main import fetch_and_store
`
- **Functions:** job, run_scheduler


## twseAnalytics/data_collector/twse_crawler.py

- **Imports (sample):** `import pandas as pd; import requests; from bs4 import BeautifulSoup
import urllib3

TWSE_URL `
- **Functions:** fetch_twse_stock_list


## twseAnalytics/data_collector/yahoo_api.py

- **Imports (sample):** `import yfinance as yf`
- **Functions:** fetch_stock_data, fetch_stock_name


## twseAnalytics/database/data_loader.py

- **Imports (sample):** `from database.db_connection import get_connection, close_connection
from database`
- **Functions:** insert_stock_price


## twseAnalytics/database/db_config.py



## twseAnalytics/database/db_connection.py

- **Imports (sample):** `import mysql.connector; from mysql.connector import Error
from database`
- **Functions:** get_connection, close_connection


## twseAnalytics/database/stock_info_manager.py

- **Imports (sample):** `from database.db_connection import get_connection, close_connection

def ensure_stock_exists`
- **Functions:** ensure_stock_exists


## twseAnalytics/main.py

- **Imports (sample):** `import sys; from datetime import datetime
import subprocess
import schedule
import time
from utils; from data_collector.yahoo_api import fetch_stock_data, fetch_stock_name
from database; from analytics.trend_analysis import analyze_stock_trend
from database`
- **Functions:** check_stock_data_exists, fetch_and_store, open_dashboard, daily_task


## twseAnalytics/setup_env.py

- **Imports (sample):** `import importlib; import subprocess; import sys`
- **Functions:** install_package, check_and_install_packages, test_yfinance, test_mysql_connection


## twseAnalytics/utils/stock_name_map.py

- **Imports (sample):** `import pandas as pd`
- **Functions:** get_stock_name


## twseAnalytics/visualization/chart_utils.py

- **Imports (sample):** `import plotly.graph_objects as go; import pandas as pd`
- **Functions:** plot_price_ma, plot_rsi, plot_macd, plot_bollinger_bands, plot_volume


## twseAnalytics/visualization/dashboard.py

- **Imports (sample):** `import streamlit as st; from main import fetch_and_store, check_stock_data_exists
from utils; from data_collector.twse_crawler import fetch_twse_stock_list

def ensure_data_completeness`
- **Functions:** ensure_data_completeness, run_dashboard

