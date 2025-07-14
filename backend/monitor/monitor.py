import datetime
import time
import logging
import pandas as pd
from prefect import task, flow
from evidently import Report
from evidently import Dataset
from evidently import DataDefinition
from evidently import Regression

# 從 evidently.metrics 匯入適合指標
from evidently.metrics import (
    DatasetMissingValueCount,
    MissingValueCount,
    DriftedColumnsCount,
    ValueDrift,
    MAE,
    RMSE,
    MinValue,
    MaxValue,
    MedianValue,
    MeanValue,
    StdValue,
    QuantileValue,
    DuplicatedRowCount,
    CategoryCount,
    UniqueValueCount,
    ScoreDistribution,
)


from src.data_loader import load_stock_data
from src.predict import Predictor
from src.create_clickhouse_table import create_clickhouse_table as create_predict_tb

from monitor.create_monitor_tb import create_clickhouse_table as create_monitor_tb
from monitor.save_result import insert_monitoring_result_to_clickhouse

logger = logging.getLogger("monitor")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():  # 避免重複加 handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

SEND_TIMEOUT = 10  # 每 10 秒執行一次

import math


def safe_float(val):
    try:
        f = float(val)
        return f if not math.isnan(f) else 0.0
    except:
        return 0.0


def extract_metric_value(metrics, metric_key_prefix: str, subkey: str = None):
    for m in metrics:
        if metric_key_prefix in m.get("metric_id", ""):
            value = m.get("value", None)
            if isinstance(value, dict):
                if subkey and subkey in value:
                    return safe_float(value[subkey])
                if "mean" in value:
                    return safe_float(value["mean"])
            return safe_float(value)
    return 0.0


def create_evidently_report():
    return Report(
        metrics=[
            # 資料缺失監控
            DatasetMissingValueCount(),
            MissingValueCount(column="Close"),
            MissingValueCount(column="Volume"),
            # 資料漂移與變異
            DriftedColumnsCount(),
            ValueDrift(column="Close"),
            ValueDrift(column="Volume"),
            # 模型表現（回歸誤差）
            MAE(),
            RMSE(),
            # 重要統計數值
            MinValue(column="Close"),
            MaxValue(column="Close"),
            MedianValue(column="Close"),
            MeanValue(column="Close"),
            StdValue(column="Close"),
            QuantileValue(column="Close", quantile=0.5),  # 中位數
            # 資料品質
            DuplicatedRowCount(),
            CategoryCount(column="ticker", category="Positive"),
            CategoryCount(column="ticker", categories=["Positive", "Negative"]),
            UniqueValueCount(column="ticker"),
            # 預測結果分佈
            # ScoreDistribution(column="predicted_close"),
        ]
    )


@task
def prep_db():
    create_monitor_tb()
    create_predict_tb()


@task
def calculate_and_log_metrics(
    day_index: int,
    predictor: Predictor,
    ticker: str,
    exchange: str,
    start_date: datetime.datetime,
):
    def to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def get_data_definition() -> DataDefinition:
        return DataDefinition(
            text_columns=[],
            numerical_columns=numerical_columns,
            categorical_columns=["ticker", "exchange"],
            regression=[Regression(target="Close", prediction="predicted_close")],
        )

    def generate_reference_dataset() -> Dataset:
        df_ref = load_stock_data(ticker, exchange, ref_start, ref_end)
        if df_ref.empty:
            logging.warning(f"無足夠歷史資料作為參考，使用當日資料作為 reference")
            return current_dataset  # fallback

        df_ref["predicted_close"] = df_ref["Close"]
        df_ref = df_ref.dropna(subset=["Close", "predicted_close"])
        df_ref = to_numeric(df_ref, numerical_columns)
        return Dataset.from_pandas(df_ref, data_definition)

    # === 日期與欄位設定 ===

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

    # === 載入目前資料 ===
    df_current = load_stock_data(ticker, exchange, day_start, day_end)
    if df_current.empty:
        logging.warning(f"{day_start.date()} 無資料，跳過此日監控")
        return

    def safe_predict(d):
        try:
            pred, actual_close, msg = predictor.predict_next_close(d)
            return float(pred) if pred is not None else None
        except Exception as e:
            logging.warning(f"⚠️ 預測失敗：{d} -> {e}")
            return None

    df_current["predicted_close"] = df_current["Date"].apply(safe_predict)

    df_current = df_current.dropna(subset=["Close", "predicted_close"])
    df_current = to_numeric(df_current, numerical_columns)

    # === 建立 DataDefinition 與 Dataset ===
    data_definition = get_data_definition()
    current_dataset = Dataset.from_pandas(df_current, data_definition)
    reference_dataset = generate_reference_dataset()

    # === 生成報告與分析 ===
    report = create_evidently_report()
    snapshot = report.run(
        reference_data=reference_dataset, current_data=current_dataset
    )
    metrics = snapshot.dict()["metrics"]

    # === 抽取指標值 ===
    prediction_drift = extract_metric_value(metrics, "ValueDrift(column=Close)")
    num_drifted_columns = extract_metric_value(
        metrics, "DriftedColumnsCount", subkey="count"
    )
    share_missing_values = extract_metric_value(
        metrics, "DatasetMissingValueCount", subkey="share"
    )
    mse = extract_metric_value(metrics, "MSE")
    rmse = extract_metric_value(metrics, "RMSE")
    mae = extract_metric_value(metrics, "MAE")
    close_median = extract_metric_value(metrics, "MedianValue(column=Close)")

    # === 組裝資料寫入 ClickHouse ===
    record = {
        "timestamp": day_start,
        "ticker": ticker,
        "prediction_drift": prediction_drift,
        "num_drifted_columns": int(num_drifted_columns),
        "share_missing_values": share_missing_values,
        "mse": mse,
        "rmse": rmse,
        "mae": mae,
        "close_median": close_median,
    }

    insert_monitoring_result_to_clickhouse(record)
    print(f"{day_start.date()} 指標寫入 ClickHouse 完成")


@flow
def stock_monitoring_flow(
    ticker: str, exchange: str, start_date: datetime.datetime, days: int = 30
):
    prep_db()
    predictor = Predictor(ticker, exchange)

    last_send = datetime.datetime.now() - datetime.timedelta(seconds=SEND_TIMEOUT)

    for i in range(days):
        calculate_and_log_metrics(i, predictor, ticker, exchange, start_date)

        now = datetime.datetime.now()
        elapsed = (now - last_send).total_seconds()

        if elapsed < SEND_TIMEOUT:
            time.sleep(SEND_TIMEOUT - elapsed)

        last_send = now
        print("本次指標送出完成")


if __name__ == "__main__":
    start_monitor_date = datetime.datetime(2025, 5, 1)
    stock_monitoring_flow("AAPL", "US", start_monitor_date, days=10)
