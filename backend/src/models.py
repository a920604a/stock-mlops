from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Integer, Text, TIMESTAMP

Base = declarative_base()

class StockPrice(Base):
    __tablename__ = "stock_prices"

    Date = Column(TIMESTAMP(timezone=True), primary_key=True)
    Open = Column(Float, nullable=True)
    High = Column(Float, nullable=True)
    Low = Column(Float, nullable=True)
    Close = Column(Float, nullable=True)
    Volume = Column(Integer, nullable=True)
    Dividends = Column(Float, nullable=True)
    Stock_Splits = Column(Float, nullable=True)
    MA5 = Column(Float, nullable=True)
    MA10 = Column(Float, nullable=True)
    EMA12 = Column(Float, nullable=True)
    EMA26 = Column(Float, nullable=True)
    MACD = Column(Float, nullable=True)
    MACD_signal = Column(Float, nullable=True)
    MACD_hist = Column(Float, nullable=True)
    BB_upper = Column(Float, nullable=True)
    BB_lower = Column(Float, nullable=True)
    BB_middle = Column(Float, nullable=True)
    VOL_MA10 = Column(Float, nullable=True)
    ticker = Column(Text, nullable=True)
    exchange = Column(Text, nullable=True)
