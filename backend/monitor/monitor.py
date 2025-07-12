import datetime
import time
import logging
import pandas as pd
from prefect import task, flow
from evidently import Report
from evidently import Dataset

# 從 evidently.metrics 匯入適合指標
from evidently.metrics import (
    DatasetMissingValueCount,
    MissingValueCount,
    DriftedColumnsCount,
    ValueDrift,
    MAE,
    RMSE,
    R2Score,
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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)

SEND_TIMEOUT = 10  # 每 10 秒執行一次


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
            R2Score(),
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
    day_start = start_date + datetime.timedelta(days=day_index)
    day_end = day_start + datetime.timedelta(days=1)

    # df = load_stock_data(ticker, exchange, day_start, day_end)
    df_current = load_stock_data(ticker, exchange, day_start, day_end)
    if df_current.empty:
        logging.warning(f"{day_start.date()} 無資料，跳過此日監控")
        return

    df_current["predicted_close"] = df_current["Date"].apply(
        lambda d: predictor.predict_next_close(d)
    )
    df_current = df_current.dropna(subset=["Close", "predicted_close"])

    current_dataset = Dataset(
        data=df_current,
        cat_columns=["ticker", "exchange"],
        num_columns=[
            "open",
            "high",
            "low",
            "close",
            "volume",
            "ma5",
            "ma10",
            "ema12",
            "ema26",
            "macd",
            "macd_signal",
            "macd_hist",
            "bb_upper",
            "bb_middle",
            "bb_lower",
            "vol_ma10",
        ],
        target="close",
        prediction="predicted_close",
    )

    # 取過去一段時間作為 reference_data，這邊示範用前30天（不包含當天）
    ref_start = day_start - datetime.timedelta(days=30)
    ref_end = day_start

    df_reference = load_stock_data(ticker, exchange, ref_start, ref_end)
    reference_dataset = Dataset(
        data=df_reference,
        cat_columns=["ticker", "exchange"],
        num_columns=[
            "open",
            "high",
            "low",
            "close",
            "volume",
            "ma5",
            "ma10",
            "ema12",
            "ema26",
            "macd",
            "macd_signal",
            "macd_hist",
            "bb_upper",
            "bb_middle",
            "bb_lower",
            "vol_ma10",
        ],
        target="close",
        prediction="predicted_close",
    )

    if df_reference.empty:
        logging.warning(f"無足夠歷史資料作為參考，使用當日資料作為 reference")
        df_reference = df_current.copy()

    report = create_evidently_report()
    report.run(
        reference_data=reference_dataset,
        current_data=current_dataset,
        # column_mapping=column_mapping,
    )

    result = report.as_dict()

    # 依指標名稱逐一取得數值，以下為範例
    prediction_mae = next(
        (
            m["result"]["current"]["value"]
            for m in result["metrics"]
            if m["metric"] == "MAE"
        ),
        None,
    )
    prediction_rmse = next(
        (
            m["result"]["current"]["value"]
            for m in result["metrics"]
            if m["metric"] == "RMSE"
        ),
        None,
    )
    r2_score = next(
        (
            m["result"]["current"]["value"]
            for m in result["metrics"]
            if m["metric"] == "R2Score"
        ),
        None,
    )

    logging.info(
        f"{day_start.date()} 指標: MAE={prediction_mae:.4f}, RMSE={prediction_rmse:.4f}, R2={r2_score:.4f}"
    )

    # 整理寫入 ClickHouse 的欄位請依照你 DB schema 設計
    record = {
        "timestamp": day_start,
        "ticker": ticker,
        "mae": prediction_mae,
        "rmse": prediction_rmse,
        "r2": r2_score,
        # 其他你想紀錄的指標也可以放進 record
    }
    insert_monitoring_result_to_clickhouse(record)
    logging.info(f"{day_start.date()} 指標寫入 ClickHouse 完成")


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
        logging.info("本次指標送出完成")


if __name__ == "__main__":
    start_monitor_date = datetime.datetime(2025, 5, 1)
    stock_monitoring_flow("AAPL", "US", start_monitor_date, days=30)
