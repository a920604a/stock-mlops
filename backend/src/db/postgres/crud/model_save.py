# src/model_save.py

from datetime import datetime

from src.db.postgres.base_postgres import SessionLocal  # 回傳 SQLAlchemy Session
from src.db.postgres.models.models import ModelMetadata  # ORM 類別


def save_model_metadata(
    ticker: str,
    run_id: str,
    model_uri: str,
    features: list[str],
    model_type: str,
    train_start_date: datetime,
    train_end_date: datetime,
    shuffle: bool,
):
    """儲存模型 metadata 到 PostgreSQL"""
    session = SessionLocal()
    try:
        metadata = ModelMetadata(
            ticker=ticker,
            run_id=run_id,
            model_uri=model_uri,
            features=features,
            model_type=model_type,
            train_start_date=train_start_date,
            train_end_date=train_end_date,
            shuffle=shuffle,
        )
        session.add(metadata)
        session.commit()
        print(f"✅ Metadata for {ticker} saved to DB")
    except Exception as e:
        session.rollback()
        print(f"❌ Failed to save metadata: {e}")
        raise
    finally:
        session.close()
