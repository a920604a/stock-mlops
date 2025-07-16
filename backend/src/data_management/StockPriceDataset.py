from typing import List
from api.schemas.dataset_request import DatasetInfo
from src.db.clickhouse.reader import get_stock_price_datasets
from src.data_management.BaseDataset import BaseDataset  # 如果放在 dataset/base_dataset.py


class StockPriceDataset(BaseDataset):
    def get_name(self) -> str:
        return "stock_prices"

    def fetch_all(self) -> List[DatasetInfo]:
        result = get_stock_price_datasets()

        datasets = []
        for row in result:
            ticker_val, exchange_val, start_date, end_date, count = row
            datasets.append(
                DatasetInfo(
                    ticker=ticker_val,
                    exchange=exchange_val,
                    start_date=start_date,
                    end_date=end_date,
                    count=count,
                    parquet_ready=count > 0,
                )
            )

        return datasets
