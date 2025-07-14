import logging
from datetime import datetime
from typing import Optional

import mlflow
import pandas as pd
from src.data_loader import get_close_price, get_last_available_date, load_stock_data
from src.database_olap import client  # 你已有的 ClickHouse client
from src.database_oltp import SessionLocal
from src.model_available import list_models
from src.model_save import ModelMetadata

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # 設定顯示 INFO 以上等級的日誌
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class Predictor:
    def __init__(self, ticker: str, exchange: str):
        self.ticker = ticker
        self.exchange = exchange
        self.session = SessionLocal()

        model_list = list_models(ticker)
        if not model_list:
            raise ValueError(f"🚫 找不到 ticker={ticker} 的任何訓練模型，請先訓練")
        self.model_meta = model_list[0]  # 預設用最新一筆

        print(
            f"✅ 使用模型: ticker={self.model_meta.ticker}, features={self.model_meta.features}, model_type={self.model_meta.model_type}"
        )
        self.model = mlflow.sklearn.load_model(self.model_meta.model_uri)
        self.features = self.model_meta.features

        # self.model_meta = self._load_latest_model_meta()

    def _load_latest_model_meta(self) -> ModelMetadata:
        query = self.session.query(ModelMetadata).filter(
            ModelMetadata.ticker == self.ticker,
            ModelMetadata.features == self.features,
            ModelMetadata.model_type == self.model_type,
        )
        meta = query.order_by(ModelMetadata.created_at.desc()).first()

        if meta is None:
            logger.warning(f"🚨 找不到 ticker: {self.ticker} 的模型 metadata，請先訓練模型")
            raise ValueError(f"No trained model found for ticker '{self.ticker}'")

        print(
            f"✅ 載入模型 metadata: ticker={meta.ticker}, model_uri={meta.model_uri}, train_end_time={meta.train_end_time}"
        )
        return meta

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values("Date")
        df = df[self.features].copy()
        df = df.fillna(method="ffill").fillna(0)
        return df

    def predict_next_close(self, target_date) -> Optional[float]:
        msg = ""
        # 👉 確保 target_date 是 datetime 物件
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d %H:%M:%S")

        # 1️⃣ 找出最近的交易日
        fetch_date = get_last_available_date(target_date, self.ticker, self.exchange)

        # 2️⃣ 建立該天的完整時間區間
        fetch_start = fetch_date.replace(hour=0, minute=0, second=0, microsecond=0)
        fetch_end = fetch_date.replace(hour=23, minute=59, second=59, microsecond=0)

        print(f"✅ 取得交易資料區間：{fetch_start} ~ {fetch_end}")
        msg += f"✅ 取得交易資料區間：{fetch_start} ~ {fetch_end}\n"

        df = load_stock_data(
            self.ticker, exchange="US", start_date=fetch_start, end_date=fetch_end
        )

        if df.empty:
            print("⚠️ 無可用資料進行預測")
            msg += "⚠️ 無可用資料進行預測\n"
            return None

        X = self._prepare_features(df)
        if X.empty:
            print(f"⚠️ 特徵工程後無有效資料，無法預測 {target_date.date()}")
            msg += f"⚠️ 特徵工程後無有效資料，無法預測 {target_date.date()}\n"
            return None

        # 取前一交易日的真實收盤價
        previous_close = df["Close"].iloc[-1]

        pred = self.model.predict(X)
        predicted_price = float(pred[0])

        # 判斷漲跌
        if predicted_price > previous_close:
            change = "漲"
            change_flag = 1
        elif predicted_price < previous_close:
            change = "跌"
            change_flag = -1
        else:
            change = "平"
            change_flag = 0

        print(f"📈 使用 {fetch_start}  {fetch_end} 的資料預測 {target_date.date()} 收盤價")
        msg += f"📈 使用 {fetch_start}  {fetch_end} 的資料預測 {target_date.date()} 收盤價\n"
        actual_df = get_close_price(target_date, self.ticker, self.exchange)
        actual_close = 0

        if actual_df is None:
            print(f"🎯 預測 {self.ticker} {target_date.date()} 尚未開盤")
            msg += f"🎯 預測 {self.ticker} {target_date.date()} 尚未開盤\n"
        elif not actual_df.empty:
            actual_close = actual_df.iloc[0]["Close"]
            print(
                f"🔍 預測 {self.ticker} {target_date.date()} 收盤價為：{predicted_price:.2f}，實際收盤價為：{actual_close:.2f}"
            )
            msg += f"🔍 預測 {self.ticker} {target_date.date()} 收盤價為：{predicted_price:.2f}，實際收盤價為：{actual_close:.2f}\n"
        else:
            print(f"🎯 預測 {self.ticker} {target_date.date()} 收盤價為：{predicted_price:.2f}")
            msg += (
                f"🎯 預測 {self.ticker} {target_date.date()} 收盤價為：{predicted_price:.2f}\n"
            )

        self.log_prediction(predicted_price, target_date)

        return predicted_price, actual_close, msg

    def log_prediction(self, predicted_price: float, target_date: datetime):
        data = {
            "ticker": [self.ticker],
            "predicted_close": [predicted_price],
            "predicted_at": [datetime.utcnow()],
            "target_date": [target_date],  # 新增欄位：預測哪一天的收盤價
            "model_metadata_id": [self.model_meta.id],
        }
        df = pd.DataFrame(data)

        client.insert_df("stock_predictions", df)
        print(
            f"✅ 已記錄預測：{self.ticker} {target_date.date()} 的收盤價 = {predicted_price:.2f}"
        )


if __name__ == "__main__":
    #
    from create_clickhouse_table import create_clickhouse_table

    create_clickhouse_table()

    predictor = Predictor("AAPL", "US")
    pred_price, actual_close, msg = predictor.predict_next_close("2025-07-03 00:00:00")
