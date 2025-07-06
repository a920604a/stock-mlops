from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from src.train import (log_model_to_mlflow, prepare_features,
                       train_and_register, train_model)
from src.train_config import TrainConfig


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
        train_start_time="2025-01-01 00:00:00",
        train_end_time="2025-01-10 00:00:00",
    )
    model, rmse = train_model(X, y, config)
    # 確認模型是 RandomForestRegressor
    from sklearn.ensemble import RandomForestRegressor

    assert isinstance(model, RandomForestRegressor)
    # rmse 是浮點數且 >= 0
    assert isinstance(rmse, float) and rmse >= 0


@patch("src.train.mlflow")
@patch("src.train.save_model_metadata")
def test_log_model_to_mlflow(mock_save_meta, mock_mlflow, sample_df):
    model_mock = MagicMock()
    config = TrainConfig(
        model_type="xgboost",
        shuffle=True,
        n_estimators=100,
        feature_columns=[
            "MA5",
            "MA10",
            "EMA12",
            "EMA26",
            "MACD",
            "MACD_signal",
            "MACD_hist",
        ],
        train_start_time="2025-01-01 00:00:00",
        train_end_time="2025-06-30 00:00:00",
    )

    run_mock = MagicMock()
    run_mock.info.run_id = "fake_run_id"
    mock_mlflow.start_run.return_value.__enter__.return_value = run_mock

    ticker = "AAPL"

    log_model_to_mlflow(model_mock, ticker, config)

    mock_mlflow.set_tracking_uri.assert_called_once()
    mock_mlflow.set_experiment.assert_called_once_with("stock_price_prediction")
    mock_mlflow.log_param.assert_any_call("ticker", ticker)
    mock_mlflow.log_param.assert_any_call("features", ",".join(config.feature_columns))
    mock_mlflow.sklearn.log_model.assert_called_once_with(model_mock, "model")
    mock_mlflow.register_model.assert_called_once()
    mock_save_meta.assert_called_once()


@patch("src.train.load_stock_data")
@patch("src.train.log_model_to_mlflow")
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
        train_start_time="2025-01-01 00:00:00",
        train_end_time="2025-06-30 00:00:00",
    )

    rmse = train_and_register("AAPL", "US", config)
    # 回傳 rmse 是浮點數且 >= 0
    assert isinstance(rmse, float) and rmse >= 0
    mock_load_data.assert_called_once()
    mock_log_mlflow.assert_called_once()
