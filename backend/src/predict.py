from datetime import datetime
from src.database_oltp import SessionLocal
from src.database_olap import client  # 你已有的 ClickHouse client
import pandas as pd
import mlflow
from src.model_save import ModelMetadata
from src.data_loader import load_stock_data

class Predictor:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.session = SessionLocal()
        self.model_meta = self._load_latest_model_meta()
        self.model = mlflow.sklearn.load_model(self.model_meta.model_uri)
        self.features = self.model_meta.features

    def _load_latest_model_meta(self):
        return (
            self.session.query(ModelMetadata)
            .filter(ModelMetadata.ticker == self.ticker)
            .order_by(ModelMetadata.created_at.desc())
            .first()
        )

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values("Date")
        df = df[self.features].copy()
        df = df.fillna(method="ffill").fillna(0)
        return df

    def predict_next_close(self) -> float:
        df = load_stock_data(self.ticker, exchange="US")
        X = self._prepare_features(df)
        X_latest = X.iloc[[-1]]
        pred = self.model.predict(X_latest)
        predicted_price = float(pred[0])

        self.log_prediction(predicted_price)
        return predicted_price

    def log_prediction(self, predicted_price: float):
        data = {
            "ticker": [self.ticker],
            "predicted_close": [predicted_price],
            "predicted_at": [datetime.utcnow()],
            "model_metadata_id": [self.model_meta.id],  # 這裡記錄使用的模型ID
        }
        df = pd.DataFrame(data)
        client.insert_df("stock_predictions", df)


if __name__ == "__main__":
    # 
    from create_clickhouse_table import create_clickhouse_table
    create_clickhouse_table()
    
    
    
    predictor = Predictor("AAPL")
    
    pred_price = predictor.predict_next_close()
    print(f"Predicted next close price: {pred_price}")
