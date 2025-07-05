from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, ARRAY
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
    created_at = Column(TIMESTAMP, nullable=False)
    train_start_time = Column(TIMESTAMP, nullable=True)
    train_end_time = Column(TIMESTAMP, nullable=True)
