import os
import clickhouse_connect


def create_clickhouse_table():
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DB", "default"),
    )

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS stock_monitoring
    (
        `timestamp` DateTime,
        `ticker` String,
        `prediction_drift` Float32,
        `num_drifted_columns` UInt32,
        `share_missing_values` Float32,
        `mse` Float32,
        `mae` Float32,
        `r2` Float32,
        `close_median` Float32
    )
    ENGINE = MergeTree
    ORDER BY (ticker, timestamp)
    """

    client.command(create_table_sql)
    print("✅ ClickHouse 表 stock_monitoring 已建立（若不存在）")
