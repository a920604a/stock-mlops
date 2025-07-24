import os

import clickhouse_connect


def create_clickhouse_table():
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 9000)),  # 預設 ClickHouse TCP 端口
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DB", "default"),
    )
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS stock_predictions (
        ticker String,
        predicted_close Float64,
        predicted_at DateTime,
        target_date DateTime,
        model_metadata_id INT
    ) ENGINE = MergeTree()
    ORDER BY (ticker, predicted_at);
    """
    client.command(create_table_sql)
    print("✅ ClickHouse table created or already exists.")
