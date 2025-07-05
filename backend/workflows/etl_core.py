from prefect import flow, task
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import time
import os
from dotenv import load_dotenv
import clickhouse_connect

load_dotenv()


def create_clickhouse_table():
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DB", "default"),
    )
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS stock_prices (
        Date DateTime,
        Open Float64,
        High Float64,
        Low Float64,
        Close Float64,
        Volume UInt64,
        MA5 Float64,
        MA10 Float64,
        EMA12 Float64,
        EMA26 Float64,
        MACD Float64,
        MACD_signal Float64,
        MACD_hist Float64,
        BB_upper Float64,
        BB_middle Float64,
        BB_lower Float64,
        VOL_MA10 Float64,
        ticker String,
        exchange String
    ) ENGINE = MergeTree()
    ORDER BY (ticker, Date);
    """
    client.command(create_table_sql)
    print("✅ ClickHouse table created or already exists.")


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
def save_raw_data(
    df: pd.DataFrame, ticker: str, exchange: str, table_name: str = "raw_stock_prices"
):
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
def save_parquet(df: pd.DataFrame, ticker: str):
    os.makedirs("parquet", exist_ok=True)
    path = f"parquet/{ticker.upper()}_processed.parquet"
    df.to_parquet(path, index=False)
    print(f"📝 Parquet written to {path}")
    return path


@task
def save_processed_data(
    df: pd.DataFrame, ticker: str, exchange: str, table_name: str = "stock_prices"
):
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)

    df = df.copy()
    df["ticker"] = ticker.upper()
    df["exchange"] = exchange.upper()

    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"✅ Saved {len(df)} processed rows to '{table_name}' for {ticker}")


@task
def insert_to_clickhouse(df: pd.DataFrame, ticker: str, exchange: str):
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DB", "default"),
    )

    df = df.copy()
    df["ticker"] = ticker.upper()
    df["exchange"] = exchange.upper()
    # 日期欄位確保是 datetime64
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"])

    # ClickHouse 期望欄位型態
    # 你可依需要調整欄位型態
    df = df.astype(
        {
            "Open": "float64",
            "High": "float64",
            "Low": "float64",
            "Close": "float64",
            "Volume": "UInt64",
            "MA5": "float64",
            "MA10": "float64",
            "EMA12": "float64",
            "EMA26": "float64",
            "MACD": "float64",
            "MACD_signal": "float64",
            "MACD_hist": "float64",
            "BB_upper": "float64",
            "BB_middle": "float64",
            "BB_lower": "float64",
            "VOL_MA10": "float64",
            "exchange": "str",
        }
    )

    # 欄位順序，跟 ClickHouse 表對應
    columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "MA5",
        "MA10",
        "EMA12",
        "EMA26",
        "MACD",
        "MACD_signal",
        "MACD_hist",
        "BB_upper",
        "BB_middle",
        "BB_lower",
        "VOL_MA10",
        "ticker",
        "exchange",
    ]

    # 寫入 ClickHouse
    client.insert_df("stock_prices", df[columns])
    print(f"✅ Inserted {len(df)} rows into ClickHouse 'stock_prices' table")


@flow(name="etl_flow")
def etl_flow(ticker: str, exchange: str = "US", period: str = "1y"):

    create_clickhouse_table()  # 確保 ClickHouse 表格已建好

    print(f"🚀 ETL for {ticker} ({exchange}) started")

    raw_df = download_stock_data(ticker, period)
    save_raw_data(raw_df, ticker, exchange)

    processed_df = clean_and_transform(raw_df)

    # save_processed_data(processed_df, ticker, exchange)

    parquet_path = save_parquet(processed_df, ticker)
    insert_to_clickhouse(processed_df, ticker, exchange)

    print("🎉 ETL completed!")


# if __name__ == "__main__":
#     etl_flow("AAPL")
