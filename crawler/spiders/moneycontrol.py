import dateparser
import scrapy
from crawler.constants import load_fundamentals
from api.enums import ItemCategory
from crawler.items import MoneyControlItem
from itemloaders import ItemLoader
from datetime import datetime


class MoneycontrolSpider(scrapy.Spider):
    name = "moneycontrol"
    allowed_domains = ["moneycontrol.com"]
    counter = 0

    def start_requests(self):
        for symbol in load_fundamentals():
            yield scrapy.Request(
                symbol.moneycontrol_news_page,
                callback=self.parse,
                meta={"symbol": symbol.tradingsymbol},
            )

    def parse(self, response, **kwargs):
        articles = response.css(".MT15.PT10.PB10")

        for i, article in enumerate(articles):
            # only parse the first 2 articles
            if i >= 2:
                break

            # get the link to the article page
            link = article.css("a::attr(href)").get()
            if not link:  # It's an Ad
                continue

            # follow the link to the article page
            yield response.follow(link, callback=self.parse_article, meta=response.meta)

    # @staticmethod
    @staticmethod
    def parse_article(response):
        # ignore if redirected to home page
        if response.url == "https://www.moneycontrol.com/news/":
            return

        # ignore if it's a pro only article
        if response.css("span.pro_only"):
            return

        # we cannot yet correctly parse the date for earnings calls
        # if "/earnings/" in response.url:
        #     self.logger.info(f"Earnings call detected, data rejected. {response.url}")
        #     return

        il = ItemLoader(item=MoneyControlItem(), selector=response.css("body"))
        il.add_value("link", response.url)
        il.add_value("symbol", response.meta["symbol"])
        il.add_value("category", ItemCategory.moneycontrol_news)
        il.add_value("scraped_date", datetime.now())

        il.add_css("title", "h1.article_title::text")
        il.add_css("description", "h2.article_desc::text")

        date = dateparser.parse(" ".join(response.xpath("//*[@class='article_schedule']//text()").extract()))
        date = date or datetime.fromtimestamp(0)
        il.add_value("date", date)

        # the content is in <p> tags inside a <div> with id=contentdata
        # this will return a list of strings, which we will join (defined in items.py)
        il.add_xpath("content", "//*[@id='contentdata']//p//text()")

        yield il.load_item()
