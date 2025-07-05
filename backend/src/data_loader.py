# src/data_loader.py
import pandas as pd
from typing import Optional

from src.database_olap import client

def load_stock_data(
    ticker: str,
    exchange: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    base_query = f"""
    SELECT *
    FROM stock_prices
    WHERE ticker = '{ticker.upper()}' AND exchange = '{exchange.upper()}'
    """

    if start_date and end_date:
        base_query += f" AND Date BETWEEN '{start_date}' AND '{end_date}'"
    elif start_date:
        base_query += f" AND Date >= '{start_date}'"
    elif end_date:
        base_query += f" AND Date <= '{end_date}'"

    base_query += " ORDER BY Date"
    
    print(f"base_query {base_query}")

    df = client.query_df(base_query)
    return df
