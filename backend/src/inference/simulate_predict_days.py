# simulate_predict_30_days.py

import asyncio
import httpx
from datetime import date, timedelta, datetime
import click

BASE_URL = "http://localhost:8000"  # 可透過參數覆寫


async def post_prediction_for_day(client: httpx.AsyncClient, target_date: date, ticker: str, exchange: str):
    payload = {
        "ticker": ticker,
        "exchange": exchange,
        "target_date": target_date.isoformat()
    }
    try:
        response = await client.post(f"{BASE_URL}/api/predict/", json=payload)
        print(f"{target_date}: {response.status_code} {response.json()}")
    except Exception as e:
        print(f"Error for {target_date}: {e}")


async def run_simulation(start_date: date, days: int, ticker: str, exchange: str):
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(days):
            target = start_date + timedelta(days=i)
            tasks.append(post_prediction_for_day(client, target, ticker, exchange))
            await asyncio.sleep(0.1)  # 可依需求調整間隔

        await asyncio.gather(*tasks)


@click.command()
@click.option(
    "--start-date",
    default=date.today().isoformat(),
    help="起始日期 (YYYY-MM-DD)，預設為今天",
)
@click.option(
    "--days",
    default=30,
    help="模擬天數，預設30天",
)
@click.option(
    "--ticker",
    default="AAPL",
    help="股票代號，預設 AAPL",
)
@click.option(
    "--exchange",
    default="NASDAQ",
    help="交易所，預設 NASDAQ",
)
@click.option(
    "--base-url",
    default="http://localhost:8000",
    help="API 伺服器 URL，預設 http://localhost:8000",
)
def main(start_date, days, ticker, exchange, base_url):
    global BASE_URL
    BASE_URL = base_url
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    except Exception as e:
        print(f"日期格式錯誤: {e}")
        return

    print(
        f"開始模擬 {days} 天，從 {start_date_obj} 起，股票代號：{ticker}，交易所：{exchange}，API：{BASE_URL}"
    )
    asyncio.run(run_simulation(start_date_obj, days, ticker, exchange))


if __name__ == "__main__":
    main()
