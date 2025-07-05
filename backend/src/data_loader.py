# src/data_loader.py
import pandas as pd
from src.database_olap import client

def load_stock_data(ticker: str, exchange: str) -> pd.DataFrame:
    query = f"""
    SELECT *
    FROM stock_prices
    WHERE ticker = '{ticker.upper()}' AND exchange = '{exchange.upper()}'
    ORDER BY Date
    """
    df = client.query_df(query)
    return df
