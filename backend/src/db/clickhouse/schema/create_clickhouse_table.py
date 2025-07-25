import os

from clickhouse_driver import Client


def create_clickhouse_table():
    client = Client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(
            os.getenv("CLICKHOUSE_PORT", 9000)
        ),  # clickhouse_driver TCP port 通常是 9000
        user=os.getenv("CLICKHOUSE_USER", "default"),
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
    client.execute(create_table_sql)
    print("✅ ClickHouse table created or already exists.")
