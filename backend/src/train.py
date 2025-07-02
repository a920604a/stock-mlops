import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
import os

from dotenv import load_dotenv
load_dotenv()

def load_data():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    query = "SELECT Close, MA10 FROM stock_data"
    df = pd.read_sql(query, con=engine)
    df = df.dropna()
    return df

def train_model():
    df = load_data()
    X = df[["MA10"]]
    y = df["Close"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()

    mlflow.start_run()
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_metric("r2_score", score)
    mlflow.sklearn.log_model(model, "model")

    mlflow.end_run()

    print(f"Trained LinearRegression model with R2 score: {score:.4f}")
    return model

if __name__ == "__main__":
    train_model()
