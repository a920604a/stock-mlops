# api/routes/mlflow_model.py

import logging
from typing import Any, Dict, List

import mlflow
from fastapi import APIRouter, HTTPException, status
from mlflow.entities import Run

# )
from src.db.postgres.crud.crud import (
    create_model,
    delete_model,
    get_all_model_id,
    get_model,
    get_models,
    update_model,
)

# from api.schemas.mlflow_request import (


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mlflow")


@router.get("/models")
def read_all_models_with_mlflow() -> List[Dict[str, Any]]:
    logger.info("read_all_models_with_mlflow")

    mlflow.set_tracking_uri("http://mlflow:5000")
    results = []
    model_ids = get_all_model_id()

    logger.info(f"model_ids: {model_ids}")

    for model_id in model_ids:
        db_model = get_model(model_id)
        if db_model is None:
            logger.warning(f"Model metadata not found for ID: {model_id}")
            continue

        # 預設基本回傳欄位
        base_info = {
            "id": db_model.id,
            "ticker": db_model.ticker,
            "exchange": db_model.exchange,
            "run_id": db_model.run_id,
            "model_uri": db_model.model_uri,
            "features": db_model.features,
            "model_type": db_model.model_type,
            "val_size": db_model.val_size,
            "created_at": db_model.created_at,
            "train_start_date": db_model.train_start_date,
            "train_end_date": db_model.train_end_date,
            "shuffle": db_model.shuffle,
        }

        # 尚未訓練
        if not db_model.run_id:
            results.append(
                {
                    **base_info,
                    "is_trained": False,
                    "metrics": None,
                    "params": None,
                    "artifact_uri": None,
                }
            )
            continue

        # 已訓練，嘗試取得 MLflow 資訊
        try:
            run: Run = mlflow.get_run(db_model.run_id)
            results.append(
                {
                    **base_info,
                    "is_trained": True,
                    "metrics": run.data.metrics,
                    "params": run.data.params,
                    "artifact_uri": run.info.artifact_uri,
                }
            )
        except Exception as e:
            logger.error(
                f"[MLflow] Failed to fetch run for model_id={model_id}, run_id={db_model.run_id}: {e}"
            )
            # 還是回傳 base，但標記為 is_trained=False，避免整體失敗
            results.append(
                {
                    **base_info,
                    "is_trained": False,
                    "metrics": None,
                    "params": None,
                    "artifact_uri": None,
                }
            )

    return results


@router.get("/{model_id:int}")
def read_model_with_mlflow(model_id: int):
    logger.info(f"read_model_with_mlflow: {model_id}")

    # 從資料庫取得 model metadata
    db_model = get_model(model_id=model_id)
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model metadata not found")

    # 若尚未訓練（沒有 run_id），則直接回傳 metadata
    if not db_model.run_id:
        return {
            "id": db_model.id,
            "ticker": db_model.ticker,
            "exchange": db_model.exchange,
            "run_id": db_model.run_id,
            "model_uri": db_model.model_uri,
            "features": db_model.features,
            "model_type": db_model.model_type,
            "val_size": db_model.val_size,
            "created_at": db_model.created_at,
            "train_start_date": db_model.train_start_date,
            "train_end_date": db_model.train_end_date,
            "shuffle": db_model.shuffle,
            "is_trained": False,
            "metrics": None,
            "params": None,
            "artifact_uri": None,
        }

    try:
        mlflow.set_tracking_uri("http://mlflow:5000")
        run: Run = mlflow.get_run(db_model.run_id)

        result = {
            "id": db_model.id,
            "ticker": db_model.ticker,
            "exchange": db_model.exchange,
            "run_id": db_model.run_id,
            "model_uri": db_model.model_uri,
            "features": db_model.features,
            "model_type": db_model.model_type,
            "val_size": db_model.val_size,
            "created_at": db_model.created_at,
            "train_start_date": db_model.train_start_date,
            "train_end_date": db_model.train_end_date,
            "shuffle": db_model.shuffle,
            "is_trained": False,
            "metrics": run.data.metrics,
            "params": run.data.params,
            "artifact_uri": run.info.artifact_uri,
        }

        logger.info(f"read_model_with_mlflow result: {result}")
        return result

    except Exception as e:
        logger.error(f"MLflow run fetch failed for run_id={db_model.run_id}: {e}")
        raise HTTPException(status_code=500, detail="讀取 MLflow 訓練資訊失敗")
