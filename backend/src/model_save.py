# backend/src/model_save.py

from src.models import ModelMetadata  # ORM 類別
from src.database_oltp import SessionLocal  # 回傳 SQLAlchemy Session

def save_model_metadata(
    ticker: str,
    run_id: str,
    model_uri: str,
    features: list[str],
    rmse: float,
):
    """儲存模型 metadata 到 PostgreSQL"""
    session = SessionLocal()
    try:
        metadata = ModelMetadata(
            ticker=ticker,
            run_id=run_id,
            model_uri=model_uri,
            features=features,
            rmse=rmse
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
