from clickhouse_driver import Client
import os


def create_clickhouse_table():
    client = Client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 9000)),  # clickhouse_driver 預設 port 9000
        user=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DB", "default"),
    )
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS stock_alerts (
        ticker String,
        alert_type String,
        alert_time DateTime,
        messages Array(String),
        target_date DateTime
    ) ENGINE = MergeTree()
    ORDER BY (ticker, alert_time);
    """
    client.execute(create_table_sql)
    print("✅ ClickHouse table created or already exists.")
