import datetime
import time
import pandas as pd
from prefect import task, flow
from evidently import Dataset, DataDefinition, Regression
from src.db.clickhouse.reader import load_stock_data
from src.inference.predict import Predictor
from src.db.clickhouse.schema.create_clickhouse_table import (
    create_clickhouse_table as create_predict_tb,
)
from monitor.db.create_monitor_tb import create_clickhouse_table as create_monitor_tb
from monitor.db.save_result import insert_monitoring_result_to_clickhouse
from monitor.config import logger, SEND_TIMEOUT
from monitor.metrics_utils import create_evidently_report, extract_metric_value
from monitor.kafka_producer import send_to_kafka, init_kafka_producer, producer
import asyncio


def to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@task
def prep_db():
    create_monitor_tb()
    create_predict_tb()


@task
async def calculate_and_log_metrics(
    day_index: int,
    predictor: Predictor,
    ticker: str,
    exchange: str,
    start_date: datetime.datetime,
):
    numerical_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "MA5",
        "MA10",
        "EMA12",
        "EMA26",
        "MACD",
        "MACD_signal",
        "MACD_hist",
        "BB_upper",
        "BB_middle",
        "BB_lower",
        "VOL_MA10",
        "predicted_close",
    ]

    day_start = start_date + datetime.timedelta(days=day_index)
    day_end = day_start + datetime.timedelta(days=1)
    ref_start = day_start - datetime.timedelta(days=30)
    ref_end = day_start

    df_current = load_stock_data(ticker, exchange, day_start, day_end)
    if df_current.empty:
        logger.warning(f"{day_start.date()} 無資料，跳過此日監控")
        return

    def safe_predict(d):
        try:
            pred, _, _ = predictor.predict_next_close(d)
            return float(pred) if pred is not None else None
        except Exception as e:
            logger.warning(f"⚠️ 預測失敗：{d} -> {e}")
            return None

    df_current["predicted_close"] = df_current["Date"].apply(safe_predict)
    df_current = df_current.dropna(subset=["Close", "predicted_close"])
    df_current = to_numeric(df_current, numerical_columns)

    data_definition = DataDefinition(
        text_columns=[],
        numerical_columns=numerical_columns,
        categorical_columns=["ticker", "exchange"],
        regression=[Regression(target="Close", prediction="predicted_close")],
    )
    current_dataset = Dataset.from_pandas(df_current, data_definition)

    df_ref = load_stock_data(ticker, exchange, ref_start, ref_end)
    if df_ref.empty:
        logger.warning("無足夠歷史資料作為參考，使用當日資料作為 reference")
        reference_dataset = current_dataset
    else:
        df_ref["predicted_close"] = df_ref["Close"]
        df_ref = df_ref.dropna(subset=["Close", "predicted_close"])
        df_ref = to_numeric(df_ref, numerical_columns)
        reference_dataset = Dataset.from_pandas(df_ref, data_definition)

    report = create_evidently_report()
    snapshot = report.run(
        reference_data=reference_dataset, current_data=current_dataset
    )
    metrics = snapshot.dict()["metrics"]

    record = {
        "timestamp": day_start,  # 保留 datetime 物件，給 ClickHouse 用
        "ticker": ticker,
        "prediction_drift": extract_metric_value(metrics, "ValueDrift(column=Close)"),
        "num_drifted_columns": int(
            extract_metric_value(metrics, "DriftedColumnsCount", subkey="count")
        ),
        "share_missing_values": extract_metric_value(
            metrics, "DatasetMissingValueCount", subkey="share"
        ),
        "mse": extract_metric_value(metrics, "MSE"),
        "rmse": extract_metric_value(metrics, "RMSE"),
        "mae": extract_metric_value(metrics, "MAE"),
        "close_median": extract_metric_value(metrics, "MedianValue(column=Close)"),
    }

    insert_monitoring_result_to_clickhouse(record)
    logger.info(f"{day_start.date()} 指標寫入 ClickHouse 完成")

    # 轉換成 Kafka 用的字串格式資料
    kafka_record = record.copy()
    kafka_record["timestamp"] = day_start.isoformat()

    # Kafka 推送
    await send_to_kafka("stock_monitoring_topic", kafka_record)
    logger.info(f"{day_start.date()} 指標推送到 Kafka 完成")


@flow
async def stock_monitoring_flow(
    ticker: str, exchange: str, start_date: datetime.datetime, days: int = 30
):
    prep_db()
    predictor = Predictor(ticker, exchange)

    # 初始化 Kafka Producer
    await init_kafka_producer()

    last_send = datetime.datetime.now() - datetime.timedelta(seconds=SEND_TIMEOUT)

    for i in range(days):
        await calculate_and_log_metrics(i, predictor, ticker, exchange, start_date)
        now = datetime.datetime.now()
        elapsed = (now - last_send).total_seconds()
        if elapsed < SEND_TIMEOUT:
            await asyncio.sleep(SEND_TIMEOUT - elapsed)
        last_send = now
        logger.info("本次指標送出完成")

    # 關閉 Kafka producer
    if producer:
        await producer.stop()
