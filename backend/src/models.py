# backend/src/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, Date, String

Base = declarative_base()

class StockData(Base):
    __tablename__ = "stock_data"

    Date = Column(Date, primary_key=True)
    Open = Column(Float)
    High = Column(Float)
    Low = Column(Float)
    Close = Column(Float)
    Volume = Column(Integer)
    MA10 = Column(Float)
