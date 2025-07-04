# backend/src/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, Date, Text

Base = declarative_base()

class StockData(Base):
    __tablename__ = "stock_prices"

    Date = Column(Date, primary_key=True)
    Open = Column(Float)
    High = Column(Float)
    Low = Column(Float)
    Close = Column(Float)
    Volume = Column(Integer)
    MA10 = Column(Float)
    Ticker = Column(Text)
    Exchange = Column(Text)
