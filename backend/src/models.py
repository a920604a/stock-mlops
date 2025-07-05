from sqlalchemy import Column, Integer, String, Float, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    run_id = Column(String, nullable=False)
    model_uri = Column(String, nullable=False)
    features = Column(ARRAY(String), nullable=False)
    rmse = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
