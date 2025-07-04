from src.train import train_and_register

def test_train_and_register():
    rmse = train_and_register("AAPL", "US")
    assert rmse > 0 and rmse < 1000  # RMSE 不該是爆炸的
