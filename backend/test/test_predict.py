from src.predict import Predictor

def test_predict():
    predictor = Predictor()
    result = predictor.predict_next_close(200.0)
    assert isinstance(result, float)
    assert result > 0
