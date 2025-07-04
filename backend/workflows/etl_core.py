from prefect import flow, task
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import time
import os
from dotenv import load_dotenv

load_dotenv()

@task(retries=3, retry_delay_seconds=10)
def download_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    attempt = 0
    while attempt < 3:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period).reset_index()
            if df.empty:
                raise ValueError(f"No data found for ticker: {ticker}")
            return df
        except Exception as e:
            attempt += 1
            print(f"❌ Attempt {attempt} failed for {ticker}: {e}")
            time.sleep(10)
    raise RuntimeError(f"Failed to download stock data for {ticker} after 3 retries")

@task
def save_raw_data(df: pd.DataFrame, ticker: str, exchange: str, table_name: str = "raw_stock_prices"):
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)

    df = df.copy()
    df["ticker"] = ticker.upper()
    df["exchange"] = exchange.upper()

    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"✅ Saved {len(df)} raw rows to '{table_name}' for {ticker}")

def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("Date").reset_index(drop=True)

    # 基本技術指標
    df["MA5"] = df["Close"].rolling(window=5).mean()
    df["MA10"] = df["Close"].rolling(window=10).mean()

    # 指數移動平均（EMA）
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()

    # MACD 及信號線
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_hist"] = df["MACD"] - df["MACD_signal"]

    # Bollinger Bands (20日)
    ma20 = df["Close"].rolling(window=20).mean()
    std20 = df["Close"].rolling(window=20).std()
    df["BB_upper"] = ma20 + (2 * std20)
    df["BB_lower"] = ma20 - (2 * std20)
    df["BB_middle"] = ma20

    # 成交量移動平均
    df["VOL_MA10"] = df["Volume"].rolling(window=10).mean()

    df = df.dropna().reset_index(drop=True)
    return df

@task
def clean_and_transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
    df = compute_technical_indicators(df)
    return df

@task
def save_processed_data(df: pd.DataFrame, ticker: str, exchange: str, table_name: str = "stock_prices"):
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)

    df = df.copy()
    df["ticker"] = ticker.upper()
    df["exchange"] = exchange.upper()

    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"✅ Saved {len(df)} processed rows to '{table_name}' for {ticker}")

@flow(name="etl_flow")
def etl_flow(ticker: str, exchange: str = "US", period: str = "1y"):
    print(f"🚀 ETL for {ticker} ({exchange}) started")

    raw_df = download_stock_data(ticker, period)
    save_raw_data(raw_df, ticker, exchange)

    processed_df = clean_and_transform(raw_df)
    save_processed_data(processed_df, ticker, exchange)

    print("🎉 ETL completed!")

# if __name__ == "__main__":
#     etl_flow("AAPL")
