from datetime import datetime, timedelta
from src.database_oltp import SessionLocal
from src.database_olap import client  # 你已有的 ClickHouse client
import pandas as pd
import mlflow
from src.model_save import ModelMetadata
from src.data_loader import load_stock_data
import logging

logger = logging.getLogger(__name__)

class Predictor:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.session = SessionLocal()
        self.model_meta = self._load_latest_model_meta()
        print(f"model_meta model_uri {self.model_meta.model_uri}")
        print(f"model_meta features {self.model_meta.features}")
        self.model = mlflow.sklearn.load_model(self.model_meta.model_uri)
        self.features = self.model_meta.features

    
    def _load_latest_model_meta(self) -> ModelMetadata:
        query = self.session.query(ModelMetadata).filter(
            ModelMetadata.ticker == self.ticker,
            ModelMetadata.features == features,
            ModelMetadata.model_type == model_type
        )
        meta = query.order_by(ModelMetadata.created_at.desc()).first()
        

        if meta is None:
            logger.warning(f"🚨 找不到 ticker: {self.ticker} 的模型 metadata，請先訓練模型")
            raise ValueError(f"No trained model found for ticker '{self.ticker}'")

        logger.info(
            f"✅ 載入模型 metadata: ticker={meta.ticker}, model_uri={meta.model_uri}, train_end_time={meta.train_end_time}"
        )
        return meta

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values("Date")
        df = df[self.features].copy()
        df = df.fillna(method="ffill").fillna(0)
        return df

    def predict_next_close(self) -> float:
        start_time = (self.train_end_time + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        df = load_stock_data(self.ticker, exchange="US")
        
        
        if df.empty:
            print("⚠️ 沒有可預測的新資料，略過預測")
            return None
        
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
    from model_available import list_available_models
    list_available_models()
    
    
    
    
    predictor = Predictor(
        ticker="AAPL",
        features=["MA5", "MA10", "EMA12", "EMA26", "MACD", "MACD_signal", "MACD_hist"],
        model_type="xgboost"
    )
    
    # pred_price = predictor.predict_next_close()
    # print(f"Predicted next close price: {pred_price}")
