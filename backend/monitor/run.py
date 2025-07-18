import datetime
import click
import asyncio
from monitor.monitor_flow import stock_monitoring_flow  # 假設這是主程式


@click.command()
@click.option("--ticker", required=True, help="股票代號 (例如: AAPL)")
@click.option("--exchange", required=True, help="交易所 (例如: US)")
@click.option(
    "--start-date",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="監控開始日期 (格式: YYYY-MM-DD)",
)
@click.option("--days", default=30, show_default=True, type=int, help="監控天數")
def cli(ticker: str, exchange: str, start_date: datetime.datetime, days: int):
    """執行股票監控流程"""
    click.echo(f"開始監控: {ticker} @ {exchange}, 起始: {start_date.date()}, 天數: {days}")
    # stock_monitoring_flow(ticker, exchange, start_date, days)
    asyncio.run(stock_monitoring_flow(ticker, exchange, start_date, days))


if __name__ == "__main__":
    cli()
# python monitor/run.py --ticker AAPL --exchange US --start-date 2025-05-01 --days 30
