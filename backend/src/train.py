import mlflow
import mlflow.sklearn
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from src.data_loader import load_stock_data

def prepare_features(df: pd.DataFrame):
    # 假設用 MA10 做示範，你可以依需求加入更多特徵
    X = df[["MA10"]].fillna(method="ffill").fillna(0)
    y = df["Close"].shift(-1).fillna(method="ffill")  # 預測下一天的收盤價
    return X[:-1], y[:-1]



def train_model(X, y):
    """訓練模型並回傳模型與驗證結果"""
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100)
    model.fit(X_train, y_train)

    preds = model.predict(X_val)
    rmse = mean_squared_error(y_val, preds) ** 0.5
    print(f"📊 Validation RMSE: {rmse:.4f}")
    return model, rmse



def log_model_to_mlflow(model, rmse, ticker):
    """將訓練好的模型與指標寫入 MLflow"""
    mlflow.set_tracking_uri("http://mlflow:5000")  # 指定你的 mlflow server URL
    mlflow.set_experiment("stock_price_prediction")
    with mlflow.start_run():
        mlflow.log_param("ticker", ticker)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, "model")
        print("✅ Model registered to MLflow")


def train_and_register(ticker: str, exchange: str):
    df = load_stock_data(ticker, exchange)
    X, y = prepare_features(df)
    model, rmse = train_model(X, y)
    log_model_to_mlflow(model, rmse, ticker)
    return rmse

if __name__ == "__main__":
    train_and_register("AAPL", "US")
