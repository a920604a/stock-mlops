from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Integer, Text, TIMESTAMP

Base = declarative_base()

class StockPrice(Base):
    __tablename__ = "stock_prices"

    Date = Column("Date", TIMESTAMP(timezone=True), primary_key=True)
    Open = Column("Open", Float, nullable=True)
    High = Column("High", Float, nullable=True)
    Low = Column("Low", Float, nullable=True)
    Close = Column("Close", Float, nullable=True)
    Volume = Column("Volume", Integer, nullable=True)
    Dividends = Column("Dividends", Float, nullable=True)
    Stock_Splits = Column("Stock Splits", Float, nullable=True)  # 這裡明確指定有空格欄位名稱
    MA5 = Column("MA5", Float, nullable=True)
    MA10 = Column("MA10", Float, nullable=True)
    EMA12 = Column("EMA12", Float, nullable=True)
    EMA26 = Column("EMA26", Float, nullable=True)
    MACD = Column("MACD", Float, nullable=True)
    MACD_signal = Column("MACD_signal", Float, nullable=True)
    MACD_hist = Column("MACD_hist", Float, nullable=True)
    BB_upper = Column("BB_upper", Float, nullable=True)
    BB_lower = Column("BB_lower", Float, nullable=True)
    BB_middle = Column("BB_middle", Float, nullable=True)
    VOL_MA10 = Column("VOL_MA10", Float, nullable=True)
    ticker = Column("ticker", Text, nullable=True)
    exchange = Column("exchange", Text, nullable=True)
