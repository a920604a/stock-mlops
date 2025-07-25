import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd

from src.inference.predict import Predictor
from src.db.postgres.crud.model_available import ModelMetadata


@pytest.fixture
def sample_model_meta():
    # 建立一個簡單的 ModelMetadata
    return ModelMetadata(
        id=1,
        ticker="AAPL",
        features=["MA5", "MA10"],
        model_type="xgboost",
        model_uri="fake_model_uri",
        train_start_date=datetime(2025, 1, 1),
        train_end_date=datetime(2025, 6, 30),
    )


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Date": pd.date_range("2025-07-01", periods=1),
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


@patch("src.inference.predict.create_clickhouse_table")
@patch("src.inference.predict.list_models")
@patch("src.inference.predict.mlflow.sklearn.load_model")
@patch("src.inference.predict.get_last_available_date")
@patch("src.inference.predict.load_stock_data")
@patch("src.inference.predict.get_close_price")
def test_predict_next_close(
    mock_get_close_price,
    mock_load_stock_data,
    mock_get_last_available_date,
    mock_load_model,
    mock_list_models,
    mock_create_table,
    sample_model_meta,
    sample_df,
    mock_model,
):
    # arrange
    mock_list_models.return_value = [sample_model_meta]
    mock_load_model.return_value = mock_model
    mock_get_last_available_date.return_value = datetime(2025, 7, 2)
    mock_load_stock_data.return_value = sample_df
    mock_get_close_price.return_value = pd.DataFrame({"Close": [151.0]})

    # act
    predictor = Predictor("AAPL", "US")
    pred_price, actual_close, msg, model_id = predictor.predict_next_close(
        "2025-07-03 00:00:00"
    )

    # assert
    assert pred_price == 152.5
    assert actual_close == 151.0
    assert "✅ 取得交易資料區間" in msg
    assert model_id == sample_model_meta.id
    mock_create_table.assert_called_once()
    mock_load_model.assert_called_once_with(sample_model_meta.model_uri)


@patch("src.inference.predict.create_clickhouse_table")
@patch("src.inference.predict.list_models")
def test_init_no_models(mock_list_models, mock_create_table):
    mock_list_models.return_value = []
    with pytest.raises(ValueError):
        Predictor("AAPL", "US")
    mock_create_table.assert_called_once()
