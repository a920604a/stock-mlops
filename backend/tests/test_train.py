from src.train import train_and_register

def test_train_and_register():
    rmse = train_and_register("AAPL", "US")
    print("RMSE:", rmse)
    assert rmse is not None, "rmse 不該是 None"
    assert 0 < rmse < 1000  # RMSE 不該是爆炸的
