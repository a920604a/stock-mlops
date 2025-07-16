# src/db/clickhouse/connection_pool.py
import threading
from queue import Queue, Empty
from clickhouse_driver import Client


class ClickhouseConnectionPool:
    def __init__(self, maxsize=5, **client_kwargs):
        self._pool = Queue(maxsize)
        self._client_kwargs = client_kwargs
        self._lock = threading.Lock()
        for _ in range(maxsize):
            self._pool.put(Client(**client_kwargs))

    def get_client(self, timeout=5):
        try:
            client = self._pool.get(timeout=timeout)
            return client
        except Empty:
            raise RuntimeError("No available ClickHouse client in pool")

    def release_client(self, client):
        self._pool.put(client)

    def __enter__(self):
        self._client = self.get_client()
        return self._client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_client(self._client)


# pool 實例，建議放在全域
clickhouse_pool = ClickhouseConnectionPool(
    maxsize=5,
    host="clickhouse",
    port=9000,
    user="default",
    password="",
    database="default",
)

# 使用範例
# def query_stock_datasets():
#     with clickhouse_pool as client:
#         sql = """
#         SELECT ticker, exchange, toString(min(Date)) AS start_date,
#             toString(max(Date)) AS end_date, count() AS count
#         FROM stock_prices
#         GROUP BY ticker, exchange
#         ORDER BY ticker, exchange
#         """
#         result = client.execute(sql)
#         return result
