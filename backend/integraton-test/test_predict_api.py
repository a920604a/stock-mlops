from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest
from api.app import app
from api.schemas.predict_request import PredictRequest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_create_prediction_success():
    # arrange
    request_data = {
        "ticker": "AAPL",
        "exchange": "NASDAQ",
        "target_date": date.today().isoformat(),
    }

    with patch("api.routes.predict.Predictor") as MockPredictor, patch(
        "api.routes.predict.send_prediction_to_kafka", return_value=None
    ):

        mock_predictor = MockPredictor.return_value
        mock_predictor.predict_next_close.return_value = (123.45, 120.00, "OK")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/predict/", json=request_data)

        assert response.status_code == 200
        assert response.json() == {"status": "submitted", "message": "預測任務已提交"}


@pytest.mark.asyncio
async def test_list_predictions_success():
    from datetime import date, datetime

    mock_df = pd.DataFrame(
        [
            {
                "ticker": "AAPL",
                "predicted_close": 123.45,
                "predicted_at": datetime(2025, 7, 22, 8, 0, 0),
                "target_date": date(2025, 7, 23),
                "model_metadata_id": 1,
            }
        ]
    )

    with patch("api.routes.predict.read_predictions", return_value=mock_df):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/predict/", params={"ticker": "AAPL"})
        print(f"response {response}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["ticker"] == "AAPL"
        assert data[0]["predicted_close"] == 123.45
