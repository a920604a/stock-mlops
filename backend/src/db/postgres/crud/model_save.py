from datetime import datetime
from src.db.postgres.base_postgres import db_session  # 改用 context manager
from src.db.postgres.models.models import ModelMetadata

from datetime import datetime
from src.db.postgres.base_postgres import db_session
from src.db.postgres.models.models import ModelMetadata


def save_or_update_model_metadata(
    id: int,
    ticker: str,
    exchange: str,
    run_id: str,
    model_uri: str,
    features: list[str],
    model_type: str,
    train_start_date: datetime,
    train_end_date: datetime,
    shuffle: bool,
):
    """儲存或更新模型 metadata 到 PostgreSQL"""
    try:
        with db_session() as session:
            metadata = session.query(ModelMetadata).filter_by(id=id).first()

            if metadata:
                # 更新現有紀錄,only save the latest training model
                # metadata.ticker = ticker
                # metadata.exchange = exchange
                metadata.run_id = run_id
                metadata.model_uri = model_uri
                metadata.features = features
                metadata.model_type = model_type
                metadata.train_start_date = train_start_date
                metadata.train_end_date = train_end_date
                metadata.shuffle = shuffle
                print(f"🔄 Metadata for {ticker}-{exchange} 已更新")
            else:
                # 新增紀錄
                metadata = ModelMetadata(
                    ticker=ticker,
                    exchange=exchange,
                    run_id=run_id,
                    model_uri=model_uri,
                    features=features,
                    model_type=model_type,
                    train_start_date=train_start_date,
                    train_end_date=train_end_date,
                    shuffle=shuffle,
                )
                session.add(metadata)
                print(f"✅ Metadata for {ticker}-{exchange} 已新增")

    except Exception as e:
        print(f"❌ Failed to save/update metadata: {e}")
        raise
