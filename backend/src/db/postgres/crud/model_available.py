from typing import List, Optional
from src.db.postgres.base_postgres import db_session  # 使用 context manager
from src.db.postgres.crud.model_save import ModelMetadata


def list_models(ticker: Optional[str] = None) -> List[ModelMetadata]:
    with db_session() as session:
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
            features_str = (
                meta.features
                if isinstance(meta.features, str)
                else ",".join(meta.features)
            )
            print(
                f"- ticker={meta.ticker:<6} "
                f"model={meta.model_type:<10} "
                f"features=[{features_str}] "
                f"trained_at={meta.train_start_date.date()} ~ {meta.train_end_date.date()}"
            )

        return results
