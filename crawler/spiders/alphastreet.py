from datetime import datetime
import scrapy
import logging
from itemloaders import ItemLoader
from crawler.constants import load_fundamentals

from api.enums import ItemCategory
from crawler.items import AlphaStreetItem


# Maximum number of pages to scrape for each symbol
MAX_PAGES = 10

# Define the categories of the articles, based on the CSS class of the article (or url)
CATEGORIES = {
    "category-earnings-call-transcripts": ItemCategory.alphastreet_concall_transcripts,
    "category-earnings-call-highlights": ItemCategory.alphastreet_concall_insights,
    "category-earnings": ItemCategory.alphastreet_earnings,
    "category-infographics": ItemCategory.alphastreet_infographics,
    "category-stock-analysis": ItemCategory.alphastreet_stock_analysis,
    "category-research-summary": ItemCategory.alphastreet_research_summary,
    "category-research-tear-sheet": ItemCategory.alphastreet_research_tear_sheet,
    "category-ipo": ItemCategory.alphastreet_ipo,
    "post": ItemCategory.alphastreet_other,  # if nothing matches, use the default category.
}

logger = logging.getLogger(__name__)


class AlphaStreetSpider(scrapy.Spider):
    name = "alphastreet"
    allowed_domains = ["alphastreet.com"]
    symbol_url = "https://alphastreet.com/india/symbol/{}/"
    latest_news_url = "https://alphastreet.com/india/latest-news/"
    pagination_url = "page/{}/"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.full_crawl = bool(kwargs.get("full_crawl", False))

    def start_requests(self):
        # Start with the latest news page
        yield scrapy.Request(self.latest_news_url, callback=self.parse)

        # Then go to the symbol pages, but only when we're doing a full crawl; passed as "-a full_crawl=1" CLI arg
        if not self.full_crawl:
            return

        for stock in load_fundamentals():
            url = self.symbol_url.format(stock.tradingsymbol)
            yield scrapy.Request(url, callback=self.parse, meta={"page": 1, "dont_redirect": True})

    def parse(self, response, **kwargs):
        page = response.meta.get("page", 1)
        articles = response.css("article.post")
        if not articles:
            logger.warning(f"DEAD END: No articles found on {response.url}")
            return

        # Get the symbol and category from the CSS class of the article
        category = ItemCategory.alphastreet_other
        symbol = "UNKNOWN"
        for article in articles:
            for css_class in article.attrib["class"].split():
                if css_class.startswith("Tickers-"):
                    symbol = css_class.partition("-")[2].upper()
                if css_class in CATEGORIES:
                    category = CATEGORIES[css_class]

            # Pass the item into the pipeline
            il = ItemLoader(item=AlphaStreetItem(), selector=article)
            il.add_value("scraped_date", datetime.now())
            il.add_value("category", category)
            il.add_value("symbol", symbol)
            il.add_css("title", "h2 a::text")
            il.add_css("date", "time::attr(datetime)")
            il.add_css("link", "a::attr(href)")
            yield il.load_item()

        # If we have reached the maximum number of pages for the symbol, stop
        if page >= MAX_PAGES:
            return

        # Create the next page url and follow it
        if "latest-news" in response.url:
            url = self.latest_news_url + self.pagination_url.format(page + 1)
        else:
            url = self.symbol_url.format(symbol) + self.pagination_url.format(page + 1)

        yield response.follow(url, callback=self.parse, meta={"page": page + 1, "dont_redirect": True})
