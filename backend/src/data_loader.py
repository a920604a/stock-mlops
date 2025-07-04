# backend/src/data_loader.py
from src.database import SessionLocal
from src.models import StockPrice
import pandas as pd

def load_stock_data(ticker: str, exchange: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    session = SessionLocal()
    query = session.query(StockPrice).filter(
        StockPrice.ticker == ticker.upper(),
        StockPrice.exchange == exchange.upper()
    )
    if start_date:
        query = query.filter(StockPrice.Date >= start_date)
    if end_date:
        query = query.filter(StockPrice.Date <= end_date)
    
    df = pd.read_sql(query.statement, session.bind)
    session.close()
    return df