# api/routes/models.py

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

import logging
import mlflow
from mlflow.entities import Run

from api.schemas.model_request import (
    ModelMetadataCreate,
    ModelCreateResponse,
    ModelMetadataResponse,
    ModelMetadataUpdate,
)
from src.db.postgres.crud.crud import (
    get_model,
    get_models,
    create_model,
    update_model,
    delete_model,
    get_all_model_id,
)

# router = APIRouter()
router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    "/models/",
    response_model=ModelCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_model_metadata(
    model: ModelMetadataCreate,
):
    try:
        print(f"model {model}")
        new_model = create_model(model=model)
        logger.info(f"Model created: id={new_model.id}, ticker={new_model.ticker}")
        return ModelCreateResponse(id=new_model.id, message="模型註冊成功")
    except Exception as e:
        logger.error(f"Error creating model metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="創建模型元數據失敗",
        )


@router.get("/models/", response_model=List[ModelMetadataResponse])
def read_models_metadata(skip: int = 0, limit: int = 100):
    print(f"Fetching models with skip={skip}, limit={limit}")
    model_dict_list = get_models(skip=skip, limit=limit)
    return [ModelMetadataResponse(**m) for m in model_dict_list]


@router.get("/models/{model_id}", response_model=ModelMetadataResponse)
def read_model_metadata(
    model_id: int,
):
    db_model = get_model(model_id=model_id)
    if db_model is None:
        logger.warning(f"Model metadata not found: id={model_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metadata not found",
        )
    return db_model


@router.delete("/models/{model_id}", response_model=ModelMetadataResponse)
def delete_model_metadata(
    model_id: int,
):
    db_model = delete_model(model_id=model_id)
    if db_model is None:
        logger.warning(f"Attempt to delete non-existing model metadata: id={model_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metadata not found",
        )
    logger.info(f"Model metadata deleted: id={model_id}")
    return db_model
