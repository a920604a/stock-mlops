import math
from evidently import Report
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
)


def safe_float(val):
    try:
        f = float(val)
        return f if not math.isnan(f) else 0.0
    except Exception:
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
            DatasetMissingValueCount(),
            MissingValueCount(column="Close"),
            MissingValueCount(column="Volume"),
            DriftedColumnsCount(),
            ValueDrift(column="Close"),
            ValueDrift(column="Volume"),
            MAE(),
            RMSE(),
            MinValue(column="Close"),
            MaxValue(column="Close"),
            MedianValue(column="Close"),
            MeanValue(column="Close"),
            StdValue(column="Close"),
            QuantileValue(column="Close", quantile=0.5),
            DuplicatedRowCount(),
            CategoryCount(column="ticker", category="Positive"),
            CategoryCount(column="ticker", categories=["Positive", "Negative"]),
            UniqueValueCount(column="ticker"),
        ]
    )
