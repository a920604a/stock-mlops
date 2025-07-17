# backend/src/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Base schema for ModelMetadata, containing common fields
class ModelMetadataBase(BaseModel):
    ticker: str = Field(..., example="AAPL", description="股票代號")
    run_id: str = Field(..., example="model_run_20231026_123456", description="模型運行ID")
    model_uri: str = Field(
        ..., example="s3://my-bucket/models/AAPL/model.pkl", description="模型儲存URI"
    )
    features: List[str] = Field(
        ..., example=["open", "high", "low", "close"], description="訓練使用的特徵列表"
    )
    model_type: Optional[str] = Field(
        None,
        example="RandomForestClassifier",
        description="模型類型 (e.g., RandomForest, XGBoost)",
    )
    shuffle: Optional[bool] = Field(None, example=True, description="訓練時是否打亂數據")
    train_start_date: Optional[datetime] = Field(
        None, example="2020-01-01T00:00:00Z", description="訓練數據開始日期"
    )
    train_end_date: Optional[datetime] = Field(
        None, example="2023-09-30T00:00:00Z", description="訓練數據結束日期"
    )

    class Config:
        # Enable ORM mode to allow Pydantic models to be created from ORM models
        # This is useful when returning SQLAlchemy model instances directly
        from_attributes = True


# Schema for creating a new ModelMetadata entry
# Inherits from ModelMetadataBase, no additional fields needed for creation
class ModelMetadataCreate(ModelMetadataBase):
    pass


# Schema for updating an existing ModelMetadata entry
# All fields are optional as only specific fields might be updated
class ModelMetadataUpdate(BaseModel):
    ticker: Optional[str] = Field(None, example="GOOG", description="股票代號")
    run_id: Optional[str] = Field(
        None, example="model_run_20231101_098765", description="模型運行ID"
    )
    model_uri: Optional[str] = Field(
        None, example="s3://my-bucket/models/GOOG/new_model.pkl", description="模型儲存URI"
    )
    features: Optional[List[str]] = Field(
        None, example=["open", "volume"], description="訓練使用的特徵列表"
    )
    model_type: Optional[str] = Field(
        None, example="XGBoostClassifier", description="模型類型"
    )
    shuffle: Optional[bool] = Field(None, example=False, description="訓練時是否打亂數據")
    train_start_date: Optional[datetime] = Field(
        None, example="2021-01-01T00:00:00Z", description="訓練數據開始日期"
    )
    train_end_date: Optional[datetime] = Field(
        None, example="2024-01-01T00:00:00Z", description="訓練數據結束日期"
    )

    class Config:
        from_attributes = True


# Schema for ModelMetadata response, includes the auto-generated 'id' and 'created_at'
class ModelMetadataResponse(ModelMetadataBase):
    id: int = Field(..., example=1, description="模型ID")
    created_at: datetime = Field(
        ..., example="2023-10-26T10:00:00Z", description="模型建立時間"
    )

    class Config:
        orm_mode = True
