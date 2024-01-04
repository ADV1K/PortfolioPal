import time

import httpx
from itertools import chain
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import logging
import asyncio
import json

RECKON_FUNDAMENTALS_URL = "https://api.reckon.live/api/getFundamentals/?page={page}"
RECKON_FUNDAMENTALS_FILE = Path(__file__).parent / "fundamentals.json"

logger = logging.getLogger(__name__)


class StockFundamentals(BaseModel):
    id: int
    market_cap_in_cr: float
    # pe_ratio: Optional[float] = None
    # book_value: float
    # divident_yield: float
    # quarterly_sales_in_cr: float
    # quarterly_sales_growth: float
    # quarterly_profit_in_cr: float
    # quarterly_profit_growth: float
    # return_on_capital: float
    tradingsymbol: str
    # datapull_type: str
    name: str
    sector: str
    industry: str
    scraped_date: str

    # added by get_moneycontrol_urls
    moneycontrol_stock_page: Optional[str] = None
    moneycontrol_news_page: Optional[str] = None


counter = counter2 = 0


async def get_moneycontrol_urls(stock: StockFundamentals) -> StockFundamentals:
    url = "https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php"
    params = {
        "type": "1",
        "classic": "true",
        "format": "json",
        "query": stock.tradingsymbol,
    }

    global counter, counter2
    limits = httpx.Limits(max_connections=2500)
    async with httpx.AsyncClient(limits=limits) as client:
        print("welp", counter := counter + 1, stock.tradingsymbol)
        response = await client.get(url, params=params, timeout=10)
        data = response.json()
        print("unwelp", counter2 := counter2 + 1, stock.tradingsymbol)

    # if no moneycontrol page found for symbol, then exit
    stock_page = data[0]["link_src"]
    if not stock_page:
        return stock

    # get news page
    company, sc_id = stock_page.split("/")[-2:]
    news_page = f"https://www.moneycontrol.com/company-article/{company}/news/{sc_id}"

    stock.moneycontrol_stock_page = stock_page
    stock.moneycontrol_news_page = news_page
    return stock


async def download_fundamentals():
    # get fundamentals from reckon api
    urls = [RECKON_FUNDAMENTALS_URL.format(page=page) for page in range(1, 31)]
    async with httpx.AsyncClient() as client:
        # request all urls in parallel
        try:
            responses = await asyncio.gather(*(client.get(url, timeout=20) for url in urls))
        except httpx.ReadTimeout:
            logger.error("skill issu of reckon api: Read Timeout")
            return

        # parse json
        stocks = []
        for response in responses:
            try:
                items = response.json()["results"]
            except KeyError:
                continue

            for item in items:
                stocks.append(StockFundamentals(**item))

    logger.info(f"Got {len(stocks)} stocks from reckon api")

    s1 = time.time()
    # get moneycontrol urls, in a batch of 100
    for i in range(0, len(stocks), 100):
        s2 = time.time()
        batch = stocks[i : i + 100]
        result = await asyncio.gather(*(get_moneycontrol_urls(stock) for stock in batch))
        stocks[i : i + 100] = result

        print(f"Batch {i // 100 + 1} took {time.time() - s2} seconds")

        # wait 1 seconds between batches
        await asyncio.sleep(3)

    print(f"Total took {time.time() - s1} seconds")
    logger.info(f"Got moneycontrol urls for {len(stocks)} stocks")

    # sort by market cap
    stocks = sorted(stocks, key=lambda x: x.market_cap_in_cr, reverse=True)

    # save to file
    with open(RECKON_FUNDAMENTALS_FILE, "w") as f:
        j = [stock.model_dump() for stock in stocks]
        json.dump(j, f, indent=4)


def load_fundamentals() -> list[StockFundamentals]:
    items = []
    with open(RECKON_FUNDAMENTALS_FILE, "r") as f:
        data = json.load(f)
        for item in data:
            items.append(StockFundamentals(**item))
    return items


if __name__ == "__main__":
    logger.info("Downloading fundamentals")
    asyncio.run(download_fundamentals())
