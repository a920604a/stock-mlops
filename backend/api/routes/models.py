# api/routes/models.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from api.schemas.model_request import (
    ModelMetadataCreate,
    ModelMetadataResponse,
    ModelMetadataUpdate,
)
from src.db.postgres.crud.crud import (
    get_model,
    get_models,
    create_model,
    update_model,
    delete_model,
)
from src.db.postgres.base_postgres import get_db  # 用的是包裝好的 get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/models/",
    response_model=ModelMetadataResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_model_metadata(
    model: ModelMetadataCreate,
):
    try:
        new_model = create_model(model=model)
        logger.info(f"Model created: id={new_model.id}, ticker={new_model.ticker}")
        return new_model
    except Exception as e:
        logger.error(f"Error creating model metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="創建模型元數據失敗",
        )


@router.get("/models/", response_model=List[ModelMetadataResponse])
def read_models_metadata(skip: int = 0, limit: int = 100):

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


@router.put("/models/{model_id}", response_model=ModelMetadataResponse)
def update_model_metadata(
    model_id: int,
    model: ModelMetadataUpdate,
):
    db_model = update_model(model_id=model_id, model_update=model)
    if db_model is None:
        logger.warning(f"Attempt to update non-existing model metadata: id={model_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metadata not found",
        )
    logger.info(f"Model metadata updated: id={model_id}")
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
