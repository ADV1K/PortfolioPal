import scrapy
from itemloaders import ItemLoader
from ..items import AlphaStreetItem

MAX_PAGES = 10  # Maximum number of pages to scrape for each symbol
NIFTY50 = [
    "ADANIENT",
    "ADANIPORTS",
    "APOLLOHOSP",
    "ASIANPAINT",
    "AXISBANK",
    "BAJAJ-AUTO",
    "BAJFINANCE",
    "BAJAJFINSV",
    "BPCL",
    "BHARTIARTL",
    "BRITANNIA",
    "CIPLA",
    "COALINDIA",
    "DIVISLAB",
    "DRREDDY",
    "EICHERMOT",
    "GRASIM",
    "HCLTECH",
    "HDFCBANK",
    "HDFCLIFE",
    "HEROMOTOCO",
    "HINDALCO",
    "HINDUNILVR",
    "HDFC",
    "ICICIBANK",
    "ITC",
    "INDUSINDBK",
    "INFY",
    "JSWSTEEL",
    "KOTAKBANK",
    "LT",
    "M&M",
    "MARUTI",
    "NTPC",
    "NESTLEIND",
    "ONGC",
    "POWERGRID",
    "RELIANCE",
    "SBILIFE",
    "SBIN",
    "SUNPHARMA",
    "TCS",
    "TATACONSUM",
    "TATAMOTORS",
    "TATASTEEL",
    "TECHM",
    "TITAN",
    "UPL",
    "ULTRACEMCO",
    "WIPRO",
]


class AlphaStreetSpider(scrapy.Spider):
    name = "alphastreet"
    allowed_domains = ["alphastreet.com"]
    url = "https://alphastreet.com/india/symbol/{symbol}/"
    # url = "https://alphastreet.com/india/latest-news/"
    # start_urls = [url]
    pagination_url = url + "page/{page_number}/"

    # Define the categories of the articles, based on the CSS class of the article (or url)
    categories = {
        "category-earnings-call-transcripts": "concall_transcripts",
        "category-earnings-call-highlights": "concall_insights",
        "category-earnings": "earnings",
        "category-infographics": "infographics",
        "category-stock-analysis": "stock_analysis",
        "category-research-summary": "research_summary",
        "category-research-tear-sheet": "research_tear_sheet",
        "category-ipo": "ipo",
        "post": "other",  # if nothing matches, use the default category.
    }

    def start_requests(self):
        for symbol in NIFTY50:
            yield scrapy.Request(
                self.url.format(symbol=symbol),
                callback=self.parse,
                meta={"page_number": 1, "dont_redirect": True},
            )

    def parse(self, response):
        page_number = response.meta.get("page_number", 1)
        articles = response.css("article.post")
        if not articles:
            return

        # Get the symbol and category from the CSS class of the article
        category, symbol = "other", "UNKNOWN"
        for article in articles:
            for css_class in article.attrib["class"].split():
                if css_class.startswith("Tickers-"):
                    symbol = css_class.split("-")[1].upper()
                if css_class in self.categories:
                    category = self.categories[css_class]

            # Pass the item into the pipeline
            il = ItemLoader(item=AlphaStreetItem(), selector=article)
            il.add_value("category", category)
            il.add_value("symbol", symbol)
            il.add_css("title", "h2 a::text")
            il.add_css("date", "time::attr(datetime)")
            il.add_css("link", "a::attr(href)")
            yield il.load_item()

        # If we have reached the maximum number of pages for the symbol, stop
        if page_number >= MAX_PAGES:
            return

        # Go to the next page of the symbol
        yield response.follow(
            self.pagination_url.format(symbol=symbol, page_number=page_number + 1),
            callback=self.parse,
            meta={"page_number": page_number + 1, "dont_redirect": True},
        )
