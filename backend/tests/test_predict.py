from datetime import datetime
from unittest.mock import MagicMock, patch

import mlflow
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from src.model_save import ModelMetadata
from src.predict import Predictor


@pytest.fixture
def sample_model_uri(tmp_path) -> str:
    model = LinearRegression()
    X = np.random.rand(10, 2)
    y = np.random.rand(10)
    model.fit(X, y)

    # 儲存到臨時資料夾
    model_path = tmp_path / "test_model"
    mlflow.sklearn.save_model(model, path=str(model_path))
    return f"{model_path}"  # 可直接被 load_model 使用


@pytest.fixture
def sample_model_meta(sample_model_uri):
    return ModelMetadata(
        id=1,
        ticker="AAPL",
        features=["MA5", "MA10"],
        model_type="xgboost",
        model_uri=str(sample_model_uri),  # 這裡是 fixture 回傳值，轉成字串
        train_start_date=datetime(2025, 1, 1),
        train_end_date=datetime(2025, 6, 30),
    )


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Date": pd.date_range(start="2025-07-01", periods=1),
            "Close": [150],
            "MA5": [148],
            "MA10": [147],
        }
    )


@pytest.fixture
def mock_model():
    mock = MagicMock()
    mock.predict.return_value = [152.5]
    return mock


@patch("src.predict.client.insert_df")
@patch("src.predict.get_close_price")
@patch("src.predict.load_stock_data")
@patch("src.predict.get_last_available_date")
@patch("src.predict.mlflow.sklearn.load_model")
@patch("src.predict.list_models")
def test_predict_next_close(
    mock_list_models,
    mock_load_model,
    mock_get_last_date,
    mock_load_data,
    mock_get_close_price,
    mock_insert_df,
    sample_model_meta,
    sample_df,
    mock_model,
):
    # Arrange
    mock_list_models.return_value = [sample_model_meta]
    mock_load_model.return_value = mock_model
    mock_get_last_date.return_value = datetime(2025, 7, 2)
    mock_load_data.return_value = sample_df
    mock_get_close_price.return_value = pd.DataFrame({"Close": [151.0]})

    # Act
    predictor = Predictor("AAPL", "US")
    result, actual_close, msg = predictor.predict_next_close("2025-07-03 00:00:00")

    # Assert
    assert isinstance(result, float)
    assert result == 152.5
    mock_insert_df.assert_called_once()
