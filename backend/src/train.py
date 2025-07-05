import mlflow
import mlflow.sklearn
import pandas as pd
from typing import Optional
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from typing import List
from train_config import TrainConfig
from src.data_loader import load_stock_data
from src.model_save import save_model_metadata



def prepare_features(df: pd.DataFrame, features: List[str]):
    df = df.sort_values("Date")
    
    
    # 先保留 'Close' 給 y 用，再擷取 features 做 X
    y = df["Close"].shift(-1).fillna(method="ffill")
    
    df = df[features].copy()
    
    df = df.fillna(method="ffill").fillna(0)
    X = df[:-1]
    y = y[:-1]
    return X, y




def train_model(X, y, config: TrainConfig):
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, shuffle=config.shuffle
    )

    if config.model_type == "random_forest":
        model = RandomForestRegressor(
            n_estimators=config.n_estimators,
            random_state=42
        )
    elif config.model_type == "xgboost":
        model = xgb.XGBRegressor(
            objective="reg:squarederror",
            n_estimators=config.n_estimators
        )
    else:
        raise ValueError(f"Unsupported model type: {config.model_type}")

    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    rmse = mean_squared_error(y_val, preds) ** 0.5
    print(f"📊 Validation RMSE: {rmse:.4f}")
    return model, rmse



def log_model_to_mlflow(model, rmse, ticker, features, train_start_time, train_end_time):
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("stock_price_prediction")

    with mlflow.start_run() as run:
        mlflow.log_param("ticker", ticker)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_param("features", ",".join(features))
        mlflow.sklearn.log_model(model, "model")

        model_uri = f"runs:/{run.info.run_id}/model"
        mlflow.register_model(model_uri, "stock_price_prediction")

        save_model_metadata(
            ticker=ticker,
            run_id=run.info.run_id,
            model_uri=model_uri,
            features=features,
            rmse=rmse,
            train_start_time=train_start_time,
            train_end_time=train_end_time
        )

        print("✅ Model registered to MLflow")


def train_and_register(
    ticker: str,
    exchange: str,
    config: TrainConfig,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    df = load_stock_data(ticker, exchange, start_date, end_date)
    X, y = prepare_features(df, config.feature_columns)
    train_start_time = df["Date"].iloc[0]
    train_end_time = df["Date"].iloc[-1]
    model, rmse = train_model(X, y, config)
    log_model_to_mlflow(
        model,
        rmse,
        ticker,
        config.feature_columns,
        train_start_time,
        train_end_time
    )

    print(f"訓練完成，RMSE：{rmse:.4f}")
    print(f"訓練資料區間：{train_start_time} ~ {train_end_time}")
    return rmse



if __name__ == "__main__":
    config = TrainConfig(
        model_type="xgboost",
        shuffle=True,
        n_estimators=200,
        feature_columns=[
            "MA5", "MA10", "EMA12", "EMA26", "MACD", "MACD_signal", "MACD_hist"
        ],
    )
    
    train_and_register(
        "AAPL",
        "US",
        config,
        start_date="2025-01-01 00:00:00",
        end_date="2025-06-30 00:00:00"
    )
