from datetime import datetime
from typing import List, Tuple, Optional
import pandas as pd
from src.db.clickhouse.connection_pool import clickhouse_pool

import logging

logger = logging.getLogger(__name__)  # 建立 logger


def query_df(client, query: str) -> pd.DataFrame:
    data, columns = client.execute(query, with_column_types=True)
    column_names = [col[0] for col in columns]
    return pd.DataFrame(data, columns=column_names)


def load_stock_data(
    ticker: str,
    exchange: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    logger.info("load_stock_data")
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

    with clickhouse_pool as client:
        # df = client.query_df(base_query)
        df = query_df(client, base_query)
    return df


def get_last_available_date(
    target_date: datetime, ticker: str, exchange: str
) -> Optional[datetime]:
    base_query = f"""
        SELECT DISTINCT Date
        FROM stock_prices
        WHERE ticker = '{ticker.upper()}' AND exchange = '{exchange.upper()}'
        AND toDate(Date) < toDate('{target_date.strftime("%Y-%m-%d")}')
        ORDER BY Date DESC
        LIMIT 1
    """

    with clickhouse_pool as client:
        # df = client.query_df(base_query)

        df = query_df(client, base_query)

    if df.empty:
        return None
    return df.iloc[0]["Date"]


def get_close_price(
    target_date: datetime, ticker: str, exchange: str
) -> Optional[float]:
    date_str = target_date.strftime("%Y-%m-%d")
    base_query = f"""
        SELECT Close FROM stock_prices
        WHERE ticker = '{ticker}'
          AND exchange = '{exchange}'
          AND toDate(Date) = toDate('{date_str}')
        ORDER BY Date DESC
        LIMIT 1
    """

    with clickhouse_pool as client:
        # df = client.query_df(query)

        df = query_df(client, base_query)

    if df.empty:
        return None
    return df


def get_stock_price_datasets() -> List[Tuple[str, str, str, str, int]]:
    base_query = """
    SELECT
        ticker,
        exchange,
        toString(min(Date)) AS start_date,
        toString(max(Date)) AS end_date,
        count() AS count
    FROM stock_prices
    GROUP BY ticker, exchange
    ORDER BY ticker, exchange
    """

    with clickhouse_pool as client:
        # df = client.query_df(sql)

        df = query_df(client, base_query)

    return list(df.itertuples(index=False, name=None))


def read_predictions(ticker: Optional[str]):
    # 建立基本的 ClickHouse 查詢語句
    base_query = """
        SELECT
            ticker,
            predicted_close,
            predicted_at,
            target_date,
            model_metadata_id
        FROM stock_predictions
    """
    # 加條件過濾
    if ticker:
        base_query += f" WHERE ticker = '{ticker.upper()}' "

    base_query += " ORDER BY predicted_at DESC "

    with clickhouse_pool as client:
        df = query_df(client, base_query)
    return df
