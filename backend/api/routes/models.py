# api/routes/train.py
from fastapi import APIRouter, BackgroundTasks
import logging
from fastapi import HTTPException
from typing import List, Optional
from api.schemas.model_request import ModelMetadataResponse, ModelMetadataCreate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/models/",
    response_model=ModelMetadataResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_model_metadata(model: ModelMetadataCreate, db: Session = Depends(get_db)):
    """
    創建一個新的模型元數據記錄。
    """
    # You might want to add logic here to check for duplicate run_id or ticker+model_type
    # For simplicity, we'll allow duplicates for now.
    return crud.create_model(db=db, model=model)


@router.get("/models/", response_model=List[ModelMetadataResponse])
def read_models_metadata(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    獲取所有模型元數據記錄。
    支持分頁：`skip` 跳過記錄數，`limit` 返回記錄數。
    """
    models = crud.get_models(db, skip=skip, limit=limit)
    return models


@router.get("/models/{model_id}", response_model=schemas.ModelMetadataResponse)
def read_model_metadata(model_id: int, db: Session = Depends(get_db)):
    """
    根據ID獲取單個模型元數據記錄。
    如果模型不存在，則返回404。
    """
    db_model = crud.get_model(db, model_id=model_id)
    if db_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model metadata not found"
        )
    return db_model


@router.put("/models/{model_id}", response_model=schemas.ModelMetadataResponse)
def update_model_metadata(
    model_id: int, model: schemas.ModelMetadataUpdate, db: Session = Depends(get_db)
):
    """
    更新現有模型元數據記錄。
    如果模型不存在，則返回404。
    """
    db_model = crud.update_model(db, model_id=model_id, model_update=model)
    if db_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model metadata not found"
        )
    return db_model


@router.delete("/models/{model_id}", response_model=ModelMetadataResponse)
def delete_model_metadata(model_id: int, db: Session = Depends(get_db)):
    """
    刪除模型元數據記錄。
    如果模型不存在，則返回404。
    """
    db_model = crud.delete_model(db, model_id=model_id)
    if db_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model metadata not found"
        )
    return db_model


# --- API Endpoints for Prediction and Training ---
