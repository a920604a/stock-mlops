from typing import List, Optional, Union

from src.database_oltp import SessionLocal  # 回傳 SQLAlchemy Session
from src.model_save import ModelMetadata


def list_models(ticker: Optional[str] = None) -> List[ModelMetadata]:
    session = SessionLocal()

    query = session.query(ModelMetadata)

    if ticker:
        query = query.filter(ModelMetadata.ticker == ticker.upper())

    results = query.order_by(ModelMetadata.created_at.desc()).all()

    if not results:
        if ticker:
            print(f"⚠️ 找不到 {ticker} 的任何模型，請先訓練")
        else:
            print("⚠️ 尚無任何可用模型")
        return []

    header = f"📋 {ticker} 可用模型：" if ticker else "📋 可用模型清單："
    print(header)
    for meta in results:
        # 注意 features 通常是 List 或 JSON，視你的 ModelMetadata 而定
        features_str = (
            meta.features if isinstance(meta.features, str) else ",".join(meta.features)
        )
        print(
            f"- ticker={meta.ticker:<6} "
            f"model={meta.model_type:<10} "
            f"features=[{features_str}] "
            f"trained_at={meta.train_start_time.date()} ~ {meta.train_end_time.date()}"
        )

    return results
