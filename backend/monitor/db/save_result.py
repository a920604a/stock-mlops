import pandas as pd
from datetime import datetime
import clickhouse_connect
import os


def insert_monitoring_result_to_clickhouse(data: dict):
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DB", "default"),
    )

    """
    data 範例:
    {
        "timestamp": datetime_obj,
        "ticker": "AAPL",
        "prediction_drift": 0.12,
        "num_drifted_columns": 3,
        "share_missing_values": 0.01,
        "mse": 0.003,
        "mae": 0.002,
        "r2": 0.85,
        "close_median": 132.5,
    }
    """
    df = pd.DataFrame([data])
    client.insert_df("stock_monitoring", df)
    print(f"✅ 已寫入 ClickHouse：{data['ticker']} {data['timestamp']} 指標資料")
