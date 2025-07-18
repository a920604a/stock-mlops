# backend/src/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


# Schema for creating a new ModelMetadata entry
# 專用於前端註冊模型的輸入 schema
class ModelMetadataCreate(BaseModel):
    ticker: str = Field(..., example="AAPL", description="股票代號")
    exchange: str = Field(..., example="US", description="交易所")
    model_type: Optional[str] = Field(None, example="random_forest", description="模型類型")
    val_size: Optional[float] = Field(None, example=0.2, description="驗證集比例")
    features: List[str] = Field(
        ..., example=["open", "high", "low", "close"], description="訓練使用的特徵列表"
    )
    train_start_date: Optional[date]
    train_end_date: Optional[date]
    shuffle: Optional[bool] = Field(None, example=True, description="是否打亂訓練資料順序")

    class Config:
        from_attributes = True


class ModelCreateResponse(BaseModel):
    id: int
    message: str


# Schema for updating an existing ModelMetadata entry
# All fields are optional as only specific fields might be updated
class ModelMetadataUpdate(BaseModel):
    ticker: Optional[str] = Field(None, example="GOOG", description="股票代號")
    exchange: Optional[str] = Field(..., example="US", description="交易所")
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
    val_size: Optional[float] = Field(None, example=0.2, description="驗證集比例")
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
class ModelMetadataResponse(BaseModel):
    id: int = Field(..., example=1, description="模型ID")
    ticker: Optional[str] = Field(None, example="GOOG", description="股票代號")
    exchange: Optional[str] = Field(..., example="US", description="交易所")
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
    val_size: Optional[float] = Field(None, example=0.2, description="驗證集比例")
    shuffle: Optional[bool] = Field(None, example=False, description="訓練時是否打亂數據")
    train_start_date: Optional[datetime] = Field(
        None, example="2021-01-01T00:00:00Z", description="訓練數據開始日期"
    )
    train_end_date: Optional[datetime] = Field(
        None, example="2024-01-01T00:00:00Z", description="訓練數據結束日期"
    )

    created_at: datetime = Field(
        ..., example="2023-10-26T10:00:00Z", description="模型建立時間"
    )

    class Config:
        orm_mode = True


class ModelMetadataSchema(BaseModel):
    id: int
    ticker: str
    exchange: str
    run_id: str
    model_uri: str
    shuffle: Optional[bool]
    features: List[str]
    model_type: str
    val_size: float
    created_at: datetime
    train_start_date: Optional[datetime]
    train_end_date: Optional[datetime]

    class Config:
        orm_mode = True  # 啟用 ORM 模式，才能用 from_orm
