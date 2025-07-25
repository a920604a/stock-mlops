import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from api.app import app
from api.schemas.train_request import TrainRequest

# ------------------------
# 測試：提交訓練任務
# ------------------------
@pytest.mark.asyncio
async def test_submit_train_job_success():
    # 模擬 TrainRequest 輸入
    request_data = {"model_id": 123}

    # 模擬 get_model 與 Celery task
    with patch("api.routes.train.get_model") as mock_get_model, patch(
        "api.routes.train.train_model_task"
    ) as mock_train_task:
        mock_model = MagicMock()
        mock_model.dict.return_value = {"model_id": 123, "name": "TestModel"}
        mock_get_model.return_value = mock_model

        mock_task = MagicMock()
        mock_task.id = "fake-task-id"
        mock_train_task.delay.return_value = mock_task

        # 發送 API 請求
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/train/", json=request_data)
            print("DEBUG submit_train_job:", response.status_code, response.text)

        # 驗證
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["task_id"] == "fake-task-id"

        mock_get_model.assert_called_once_with(123)
        mock_train_task.delay.assert_called_once()


# ------------------------
# 測試：查詢訓練狀態 - SUCCESS
# ------------------------
@pytest.mark.asyncio
async def test_get_train_status_success():
    fake_task_id = "test-success"

    with patch("api.routes.train.AsyncResult") as mock_async_result:
        mock_result = MagicMock()
        mock_result.state = "SUCCESS"
        mock_result.result = {"accuracy": 0.95}
        mock_async_result.return_value = mock_result

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/train/status/{fake_task_id}")
            print("DEBUG get_train_status:", response.status_code, response.text)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["result"] == {"accuracy": 0.95}
        assert data["task_id"] == fake_task_id


# ------------------------
# 測試：查詢訓練狀態 - PENDING
# ------------------------
@pytest.mark.asyncio
async def test_get_train_status_pending():
    fake_task_id = "test-pending"

    with patch("api.routes.train.AsyncResult") as mock_async_result:
        mock_result = MagicMock()
        mock_result.state = "PENDING"
        mock_async_result.return_value = mock_result

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/train/status/{fake_task_id}")

        assert response.status_code == 200
        assert response.json() == {"task_id": fake_task_id, "status": "pending"}


# ------------------------
# 測試：查詢訓練狀態 - FAILURE
# ------------------------
@pytest.mark.asyncio
async def test_get_train_status_failure():
    fake_task_id = "test-failure"

    with patch("api.routes.train.AsyncResult") as mock_async_result:
        mock_result = MagicMock()
        mock_result.state = "FAILURE"
        mock_result.result = Exception("Train failed")
        mock_async_result.return_value = mock_result

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/train/status/{fake_task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert "Train failed" in data["error"]


# ------------------------
# 測試：未知狀態
# ------------------------
@pytest.mark.asyncio
async def test_get_train_status_unknown():
    fake_task_id = "test-unknown"

    with patch("api.routes.train.AsyncResult") as mock_async_result:
        mock_result = MagicMock()
        mock_result.state = "SOMETHING_WEIRD"
        mock_async_result.return_value = mock_result

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/train/status/{fake_task_id}")

        assert response.status_code == 400
        assert response.json()["detail"] == "Unknown task state"
