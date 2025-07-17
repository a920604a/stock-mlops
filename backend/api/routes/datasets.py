# api/routes/datasets.py
from fastapi import APIRouter, HTTPException
import logging
from typing import List

from api.schemas.dataset_request import DatasetInfo
from src.data_management.StockPriceDataset import StockPriceDataset

router = APIRouter()


@router.get("/datasets", response_model=List[DatasetInfo])
def get_datasets():
    try:
        print("dataset")
        dataset_source = StockPriceDataset()
        return dataset_source.fetch_all()
    except Exception as e:
        logging.error(f"Error querying datasets: {e}")
        raise HTTPException(status_code=500, detail="查詢資料集失敗")
