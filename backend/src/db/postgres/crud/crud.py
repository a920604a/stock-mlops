# backend/src/db/postgres/crud.py
from typing import List, Optional
from src.db.postgres.base_postgres import db_session

from api.schemas.model_request import (
    ModelMetadataCreate,
    ModelMetadataUpdate,
    ModelMetadataResponse,
    ModelMetadataSchema,
)

from datetime import datetime
from uuid import uuid4

from src.db.postgres.models.models import ModelMetadata  # ORM 類別

# --- CRUD Operations for ModelMetadata ---


def get_model(model_id: int) -> Optional[ModelMetadataSchema]:
    with db_session() as db:
        db_model = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
        if db_model:
            return ModelMetadataSchema.from_orm(db_model)
        return None


def get_models(skip: int = 0, limit: int = 100) -> List[dict]:
    with db_session() as db:
        models = db.query(ModelMetadata).offset(skip).limit(limit).all()
        results = []
        for m in models:
            results.append(
                {
                    "id": m.id,
                    "ticker": m.ticker,
                    "exchange": m.exchange,
                    "run_id": m.run_id,
                    "model_uri": m.model_uri,
                    "shuffle": m.shuffle,
                    "features": m.features,
                    "model_type": m.model_type,
                    "created_at": m.created_at,
                    "train_start_date": m.train_start_date,
                    "train_end_date": m.train_end_date,
                }
            )
        return results


def create_model(model: ModelMetadataCreate) -> ModelMetadata:
    with db_session() as db:
        db_model = ModelMetadata(
            ticker=model.ticker,
            exchange=model.exchange,
            model_type=model.model_type,
            features=model.features,
            train_start_date=model.train_start_date,
            train_end_date=model.train_end_date,
            shuffle=model.shuffle,
            # run_id=f"model_run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}",
            # model_uri="",  # 可先留空或預設為空字串，等訓練完成補上
            run_id="",  # 或空字串 ""
            model_uri="",  # 訓練完成後再補上
        )
        # db_model = ModelMetadata(**model.model_dump())  # Pydantic v2+
        db.add(db_model)
        db.flush()  # 先寫入DB取得 id 等自動生成欄位
        db.refresh(db_model)
        # ✅ 在 session 關閉前就轉換
        return ModelMetadataResponse.from_orm(db_model)


def update_model(
    model_id: int, model_update: ModelMetadataUpdate
) -> Optional[ModelMetadata]:
    with db_session() as db:
        db_model = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
        if not db_model:
            return None
        for key, value in model_update.model_dump(exclude_unset=True).items():
            setattr(db_model, key, value)
        db.flush()
        db.refresh(db_model)
        return db_model


def delete_model(model_id: int) -> Optional[ModelMetadata]:
    with db_session() as db:
        db_model = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
        if not db_model:
            return None
        db.delete(db_model)
        return db_model
