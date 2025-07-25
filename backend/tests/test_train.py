from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from src.train_config import TrainConfig

from src.model_training.train import (
    log_model_to_mlflow,
    prepare_features,
    train_ml_model,
    train_model,
    train_test_split,
)


@pytest.fixture
def sample_df():
    dates = pd.date_range("2025-01-01", periods=10)
    data = {
        "Date": dates,
        "Close": np.arange(10, 20),
        "MA5": np.random.rand(10),
        "MA10": np.random.rand(10),
        "EMA12": np.random.rand(10),
        "EMA26": np.random.rand(10),
        "MACD": np.random.rand(10),
        "MACD_signal": np.random.rand(10),
        "MACD_hist": np.random.rand(10),
    }
    df = pd.DataFrame(data)
    return df


def test_prepare_features(sample_df):
    features = [
        "MA5",
        "MA10",
        "EMA12",
        "EMA26",
        "MACD",
        "MACD_signal",
        "MACD_hist",
    ]
    X, y = prepare_features(sample_df, features)
    # 檢查 X, y 長度是否相同
    assert len(X) == len(y)
    # X 欄位是否符合 features
    assert list(X.columns) == features
    # y 為 Close 欄位往後移一筆且去除最後一筆
    assert y.iloc[-1] == sample_df["Close"].iloc[-1]
    # 檢查無遺漏值
    assert not X.isnull().any().any()
    assert not y.isnull().any()


def test_train_model(sample_df):
    features = [
        "MA5",
        "MA10",
        "EMA12",
        "EMA26",
        "MACD",
        "MACD_signal",
        "MACD_hist",
    ]
    X, y = prepare_features(sample_df, features)
    config = TrainConfig(
        model_type="random_forest",
        shuffle=False,
        n_estimators=10,
        feature_columns=features,
        train_start_date=datetime.strptime(
            "2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
        ).date(),
        train_end_date=datetime.strptime(
            "2025-01-10 00:00:00", "%Y-%m-%d %H:%M:%S"
        ).date(),
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=config.val_size, shuffle=config.shuffle
    )

    model, rmse = train_model(X_train, y_train, X_val, y_val, config)
    # 確認模型是 RandomForestRegressor
    from sklearn.ensemble import RandomForestRegressor

    assert isinstance(model, RandomForestRegressor)
    # rmse 是浮點數且 >= 0
    assert isinstance(rmse, float) and rmse >= 0


@patch("src.model_training.train.load_stock_data")
@patch("src.model_training.train.log_model_to_mlflow")
def test_train_and_register(mock_log_mlflow, mock_load_data, sample_df):
    mock_load_data.return_value = sample_df

    config = TrainConfig(
        model_type="xgboost",
        shuffle=True,
        n_estimators=10,
        feature_columns=[
            "MA5",
            "MA10",
            "EMA12",
            "EMA26",
            "MACD",
            "MACD_signal",
            "MACD_hist",
        ],
        train_start_date=datetime.strptime(
            "2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
        ).date(),
        train_end_date=datetime.strptime(
            "2025-06-30 00:00:00", "%Y-%m-%d %H:%M:%S"
        ).date(),
    )

    rmse, run_id = train_ml_model(0, "AAPL", "US", config)
    # 回傳 rmse 是浮點數且 >= 0
    assert isinstance(rmse, float) and rmse >= 0
    mock_load_data.assert_called_once()
    mock_log_mlflow.assert_called_once()
