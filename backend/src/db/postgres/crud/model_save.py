from datetime import datetime
from src.db.postgres.base_postgres import db_session  # 改用 context manager
from src.db.postgres.models.models import ModelMetadata


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
    try:
        with db_session() as session:
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
            # commit 由 db_session 自動處理
            print(f"✅ Metadata for {ticker} saved to DB")
    except Exception as e:
        print(f"❌ Failed to save metadata: {e}")
        raise
