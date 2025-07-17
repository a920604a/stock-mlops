from sqlalchemy import ARRAY, TIMESTAMP, Boolean, Column, Integer, String, Text, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), nullable=False)
    run_id = Column(String(100), nullable=False)
    model_uri = Column(Text, nullable=False)
    shuffle = Column(Boolean)
    features = Column(ARRAY(String), nullable=False)
    model_type = Column(String, nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())  # 這裡加上預設值
    train_start_date = Column(TIMESTAMP, nullable=True)
    train_end_date = Column(TIMESTAMP, nullable=True)
