from urllib.parse import urlencode
from datetime import datetime
import math

from itemloaders import ItemLoader
import scrapy

from crawler.items import YoutubeItem
from crawler.constants import load_fundamentals
from config import config


MAX_STOCKS = 500
MAX_STOCKS_PER_DAY = 100


class YoutubeSpider(scrapy.Spider):
    name = "youtube"
    allowed_domains = ["youtube.googleapis.com"]
    search_url = "https://youtube.googleapis.com/youtube/v3/search?"
    video_url = "https://youtube.googleapis.com/youtube/v3/videos?"

    def start_requests(self):
        # here, we're assuming that the stocks are already sorted by market cap
        stocks = load_fundamentals()[:MAX_STOCKS]

        # use modulo to distribute the requests evenly across the month
        # by sending requests for 100 stocks every day
        index = math.ceil(datetime.now().day % (MAX_STOCKS / MAX_STOCKS_PER_DAY))
        low = MAX_STOCKS_PER_DAY * index
        high = low + MAX_STOCKS_PER_DAY
        print(stocks[low], stocks[high - 1])
        for item in stocks[low:high]:
            yield self.search_request(item)

    def search_request(self, item, max_results=50):
        query = f"{item.name} stock analysis"
        params = {
            "q": query,
            "part": "id,snippet",
            "type": "youtube_video",
            "order": "relevance",
            "fields": "items(id(videoId),snippet(channelTitle,title,publishedAt)),nextPageToken",
            "maxResults": max_results,
            "key": config.YOUTUBE_API_KEY,
        }
        url = self.search_url + urlencode(params)
        meta = {
            "is_search_request": True,
            "symbol": item.tradingsymbol,
            "name": item.name,
            "sector": item.sector,
        }

        return scrapy.Request(url, callback=self.parse, meta=meta)

    def video_request(self, response):
        data = response.json()
        meta = response.meta
        del meta["is_search_request"]
        video_ids = []
        for item in data["items"]:
            video_ids.append(item["id"]["videoId"])

        params = {
            "part": "id,snippet,statistics",
            "id": ",".join(video_ids),
            "key": config.YOUTUBE_API_KEY,
        }
        url = self.video_url + urlencode(params)

        return scrapy.Request(url, callback=self.parse, meta=meta)

    def parse(self, response, **kwargs):
        if response.meta.get("is_search_request", False):  # if it is a search request
            yield self.video_request(response)  # send a youtube_video request
        else:
            yield from self.parse_video(response)

    @staticmethod
    def parse_video(response):
        data = response.json()
        for item in data["items"]:
            il = ItemLoader(item=YoutubeItem(), selector=item)

            il.add_value("scraped_date", datetime.now())
            il.add_value("link", f"https://www.youtube.com/watch?v={item['id']}")
            il.add_value("channel", item["snippet"]["channelTitle"])
            il.add_value("title", item["snippet"]["title"])
            il.add_value("date", item["snippet"]["publishedAt"])
            il.add_value("views", item["statistics"]["viewCount"])

            il.add_value("symbol", response.meta["symbol"])
            il.add_value("category", "youtube_video")
            il.add_value("name", response.meta["name"])
            il.add_value("sector", response.meta["sector"])

            yield il.load_item()
