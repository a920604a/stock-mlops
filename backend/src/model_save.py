# backend/src/model_save.py

from src.models import ModelMetadata  # ORM 類別
from src.database_oltp import SessionLocal  # 回傳 SQLAlchemy Session
from datetime import datetime


def save_model_metadata(
    ticker: str,
    run_id: str,
    model_uri: str,
    features: list[str],
    model_type: str,
    train_start_time: datetime,
    train_end_time: datetime
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
            train_start_time=train_start_time,
            train_end_time=train_end_time
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
