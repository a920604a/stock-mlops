
from src.predict import Predictor

def test_predict():
    # 先確保模型存在

    predictor = Predictor(model_uri="models:/stock_price_prediction/latest")
    result = predictor.predict_next_close(200.0)
    assert isinstance(result, float)
    assert result > 0
