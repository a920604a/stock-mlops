# src/etl/etl_runner.py
from prefect import flow
from workflows.etl_core import etl_flow  # 原本你寫的核心流程


@flow(name="etl_flow_trigger", log_prints=True)
def trigger_etl_flow(tickers: list[tuple[str, str]]):
    for ticker, exchange in tickers:
        etl_flow(ticker, exchange)
