# src/data_loader.py
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta

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


def get_last_available_date(target_date: datetime, 
                            ticker: str,
                            exchange: str
                            ) -> Optional[datetime]:
    # SQL：找 target_date 前所有資料
    base_query = f"""
        SELECT DISTINCT Date
        FROM stock_prices
        WHERE ticker = '{ticker.upper()}' AND exchange = '{exchange.upper()}'
        AND toDate(Date) < toDate('{target_date.strftime("%Y-%m-%d")}')
        ORDER BY Date DESC
        LIMIT 1
    """
    print(f"base_query {base_query}")

    df = client.query_df(base_query)

    if df.empty:
        return None
    # 回傳最接近 target_date 的那天
    return df.iloc[0]['Date']



def get_close_price(target_date: datetime, ticker: str, exchange: str) -> Optional[float]:
    date_str = target_date.strftime("%Y-%m-%d")
    """
    查詢指定股票與日期的實際收盤價，若無資料則回傳 None。
    """
    query = f"""
        SELECT Close FROM stock_prices
        WHERE ticker = '{ticker}'
          AND exchange = '{exchange}'
          AND toDate(Date) = toDate('{date_str}')
        ORDER BY Date DESC
        LIMIT 1
    """
    df = client.query_df(query)
    print(f"base_query {query}")
    if df.empty:
        return None
    return df