from src.models import ModelMetadata  # ORM 類別
from src.database_oltp import SessionLocal  # 回傳 SQLAlchemy Session


def list_available_models():
    session = SessionLocal()
    results = (
        session.query(
            ModelMetadata.ticker,
            ModelMetadata.features,
            ModelMetadata.model_type
        )
        .order_by(ModelMetadata.created_at.desc())
        .all()
    )

    print("📋 可用模型清單：")
    for row in results:
        print(f"- ticker={row.ticker}, model={row.model_type}, features={row.features}, time={row.train_start_time.date()}~{row.train_end_time.date()}")
