from prefect import flow
from etl_core import etl_flow


@flow(name="etl_flow_with_schedule", log_prints=True)
def etl_flow_with_schedule():
    tickers = [("AAPL", "US"), ("TSM", "US"), ("2330.TW", "TW")]
    for ticker, exchange in tickers:
        etl_flow(ticker, exchange)


if __name__ == "__main__":
    etl_flow_with_schedule()
