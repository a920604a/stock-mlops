import logging
from datetime import datetime
from typing import Optional

import mlflow.sklearn
import pandas as pd
from src.db.clickhouse.reader import (
    get_close_price,
    get_last_available_date,
    load_stock_data,
)
from src.db.clickhouse.base_clickhouse import client  # 你已有的 ClickHouse client
from src.db.postgres.base_postgres import db_session
from src.db.postgres.crud.model_available import list_models
from src.db.postgres.crud.model_save import ModelMetadata

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class Predictor:
    def __init__(self, ticker: str, exchange: str):
        self.ticker = ticker
        self.exchange = exchange

        # 使用 context manager 取得 session
        with db_session() as session:
            model_list = list_models(ticker)
            if not model_list:
                raise ValueError(f"🚫 找不到 ticker={ticker} 的任何訓練模型，請先訓練")
            self.model_meta = model_list[0]  # 預設用最新一筆

        logger.info(
            f"✅ 使用模型: ticker={self.model_meta.ticker}, features={self.model_meta.features}, model_type={self.model_meta.model_type}"
        )

        try:
            self.model = mlflow.sklearn.load_model(self.model_meta.model_uri)
        except Exception as e:
            logger.error(f"❌ 載入模型失敗: {e}")
            raise

        self.features = self.model_meta.features

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values("Date")
        df = df[self.features].copy()
        df = df.fillna(method="ffill").fillna(0)
        return df

    def predict_next_close(self, target_date) -> Optional[tuple[float, float, str]]:
        msg = ""
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d %H:%M:%S")

        fetch_date = get_last_available_date(target_date, self.ticker, self.exchange)
        fetch_start = fetch_date.replace(hour=0, minute=0, second=0, microsecond=0)
        fetch_end = fetch_date.replace(hour=23, minute=59, second=59, microsecond=0)

        logger.info(f"✅ 取得交易資料區間：{fetch_start} ~ {fetch_end}")
        msg += f"✅ 取得交易資料區間：{fetch_start} ~ {fetch_end}\n"

        df = load_stock_data(
            self.ticker,
            exchange=self.exchange,
            start_date=fetch_start,
            end_date=fetch_end,
        )

        if df.empty:
            logger.warning("⚠️ 無可用資料進行預測")
            msg += "⚠️ 無可用資料進行預測\n"
            return None

        X = self._prepare_features(df)
        if X.empty:
            logger.warning(f"⚠️ 特徵工程後無有效資料，無法預測 {target_date.date()}")
            msg += f"⚠️ 特徵工程後無有效資料，無法預測 {target_date.date()}\n"
            return None

        previous_close = df["Close"].iloc[-1]
        pred = self.model.predict(X)
        predicted_price = float(pred[0])

        if predicted_price > previous_close:
            change_flag = 1
        elif predicted_price < previous_close:
            change_flag = -1
        else:
            change_flag = 0

        logger.info(f"📈 使用 {fetch_start} ~ {fetch_end} 的資料預測 {target_date.date()} 收盤價")
        msg += f"📈 使用 {fetch_start} ~ {fetch_end} 的資料預測 {target_date.date()} 收盤價\n"

        actual_df = get_close_price(target_date, self.ticker, self.exchange)
        actual_close = 0

        if actual_df is None or actual_df.empty:
            logger.info(f"🎯 預測 {self.ticker} {target_date.date()} 尚未開盤")
            msg += f"🎯 預測 {self.ticker} {target_date.date()} 尚未開盤\n"
        else:
            actual_close = actual_df.iloc[0]["Close"]
            logger.info(
                f"🔍 預測 {self.ticker} {target_date.date()} 收盤價為：{predicted_price:.2f}，實際收盤價為：{actual_close:.2f}"
            )
            msg += f"🔍 預測 {self.ticker} {target_date.date()} 收盤價為：{predicted_price:.2f}，實際收盤價為：{actual_close:.2f}\n"

        self.log_prediction(predicted_price, target_date)

        return predicted_price, actual_close, msg

    def log_prediction(self, predicted_price: float, target_date: datetime):
        data = {
            "ticker": [self.ticker],
            "predicted_close": [predicted_price],
            "predicted_at": [datetime.utcnow()],
            "target_date": [target_date],
            "model_metadata_id": [self.model_meta.id],
        }
        df = pd.DataFrame(data)
        client.insert_df("stock_predictions", df)
        logger.info(
            f"✅ 已記錄預測：{self.ticker} {target_date.date()} 的收盤價 = {predicted_price:.2f}"
        )


if __name__ == "__main__":
    from src.db.clickhouse.schema.create_clickhouse_table import create_clickhouse_table

    create_clickhouse_table()

    predictor = Predictor("AAPL", "US")
    pred_price, actual_close, msg = predictor.predict_next_close("2025-07-03 00:00:00")
    print(msg)
