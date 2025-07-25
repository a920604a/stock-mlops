from dataclasses import dataclass, field
from datetime import date
from typing import List, Literal

FEATURE_COLUMNS = [
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
]


@dataclass
class TrainConfig:
    model_type: Literal["xgboost", "random_forest"] = "random_forest"
    feature_columns: List[str] = field(default_factory=lambda: FEATURE_COLUMNS)
    val_size: float = 0.2
    shuffle: bool = False
    n_estimators: int = 100
    train_start_date: date = None
    train_end_date: date = None
