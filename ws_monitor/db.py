from clickhouse_driver import Client
from datetime import datetime

client = Client(host="clickhouse")


async def insert_prediction_to_clickhouse(prediction: dict):
    from concurrent.futures import ThreadPoolExecutor
    import asyncio

    def to_datetime(value):
        # 確保 value 是 datetime 物件

        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                # 如果有微秒 + Z 或其他格式不兼容，手動處理
                return datetime.strptime(value.split("Z")[0], "%Y-%m-%dT%H:%M:%S.%f")
        raise TypeError(f"Unsupported datetime value: {value}")

    def sync_insert():
        predicted_at = to_datetime(prediction["predicted_at"])
        target_date = to_datetime(prediction["target_date"])

        client.execute(
            """
            INSERT INTO default.stock_predictions
            (ticker, predicted_close, predicted_at, target_date, model_metadata_id)
            VALUES
            """,
            [
                (
                    prediction["ticker"],
                    float(prediction["predicted_close"]),
                    predicted_at,
                    target_date,
                    int(prediction.get("model_metadata_id", 0)),
                )
            ],
        )

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(ThreadPoolExecutor(), sync_insert)
