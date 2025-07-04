import mlflow.sklearn
import numpy as np
import pandas as pd

class Predictor:
    def __init__(self, model_uri="models:/stock_price_prediction/latest"):
        self.model = mlflow.sklearn.load_model(model_uri)

    def predict_next_close(self, ma10_value: float) -> float:
        X = np.array([[ma10_value]])
        pred = self.model.predict(X)
        return float(pred[0])

if __name__ == "__main__":
    predictor = Predictor()
    example_ma10 = 150.0
    pred_price = predictor.predict_next_close(example_ma10)
    print(f"Predicted next close price: {pred_price}")
