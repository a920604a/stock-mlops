from abc import ABC, abstractmethod
from typing import List

from api.schemas.dataset_request import DatasetInfo


class BaseDataset(ABC):
    @abstractmethod
    def fetch_all(self) -> List[DatasetInfo]:
        pass

    @abstractmethod
    def get_name(self) -> str:
        """回傳資料來源名稱，例如 stock_prices"""
        pass
