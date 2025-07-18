from backend.src.db.clickhouse.reader import load_stock_data


def test_load_stock_data():
    df = load_stock_data("AAPL", "US")
    assert not df.empty
    assert "Close" in df.columns
