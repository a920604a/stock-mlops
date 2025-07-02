from fastapi import FastAPI
from pydantic import BaseModel
import mlflow.sklearn
import numpy as np

app = FastAPI()

class PredictRequest(BaseModel):
    MA10: float

# 載入模型（可在啟動時）
model = mlflow.sklearn.load_model("models:/model/latest")  # 需確保 mlflow model registry 路徑正確

@app.post("/predict")
def predict(data: PredictRequest):
    X = np.array([[data.MA10]])
    pred = model.predict(X)
    return {"predicted_close": float(pred[0])}
