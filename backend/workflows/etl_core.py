from prefect import flow, task
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import time
import os
from dotenv import load_dotenv

load_dotenv()
# yf.enable_debug_mode()



@task(retries=3, retry_delay_seconds=10)
def download_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    從 Yahoo Finance 下載股票資料，失敗時會重試
    """
    attempt = 0
    while attempt < 3:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period).reset_index()
            if df.empty:
                raise ValueError("No data found for ticker: " + ticker)
            return df
        except Exception as e:
            attempt += 1
            print(f"❌ Attempt {attempt} failed for {ticker}: {e}")
            time.sleep(10)
    raise RuntimeError(f"Failed to download stock data for {ticker} after 3 retries")

@task
def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清理資料並新增技術指標（如 MA10）
    """
    df = df.dropna()
    df["MA10"] = df["Close"].rolling(window=10).mean()
    return df


@task
def save_to_postgres(df: pd.DataFrame, ticker: str, exchange: str, table_name: str = "stock_prices"):
    """
    儲存資料至 PostgreSQL，附加欄位 ticker、exchange
    """
    DATABASE_URL = os.getenv("DATABASE_URL")  # postgresql://user:password@db:5432/stocks
    engine = create_engine(DATABASE_URL)

    df["ticker"] = ticker.upper()
    df["exchange"] = exchange.upper()

    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"✅ Saved {len(df)} rows to table '{table_name}' for {ticker}")


@flow(name="etl_flow")
def etl_flow(ticker: str, exchange: str = "US", period: str = "1y"):
    """
    完整 ETL 流程：下載 → 清理 → 儲存
    """
    print(f"🚀 ETL for {ticker} ({exchange}) started")
    raw_data = download_stock_data(ticker, period)
    clean_data = clean_stock_data(raw_data)
    save_to_postgres(clean_data, ticker, exchange)
    # print(clean_data.tail())

