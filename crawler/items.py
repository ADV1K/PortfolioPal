from datetime import datetime

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Join, Compose
import dateparser


class AlphaStreetItem(scrapy.Item):
    link = scrapy.Field(output_processor=TakeFirst())
    short_code = scrapy.Field(output_processor=TakeFirst())
    symbol = scrapy.Field(output_processor=TakeFirst())
    category = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    date = scrapy.Field(
        default=datetime.fromtimestamp(0),
        input_processor=MapCompose(dateparser.parse),
        output_processor=TakeFirst(),
    )
    scraped_date = scrapy.Field(output_processor=TakeFirst())


class YoutubeItem(scrapy.Item):
    symbol = scrapy.Field(output_processor=TakeFirst())
    category = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    sector = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    short_code = scrapy.Field(output_processor=TakeFirst())
    channel = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    views = scrapy.Field(output_processor=TakeFirst())
    date = scrapy.Field(input_processor=MapCompose(dateparser.parse), output_processor=TakeFirst())
    scraped_date = scrapy.Field(output_processor=TakeFirst())


class MoneyControlItem(scrapy.Item):
    link = scrapy.Field(output_processor=TakeFirst())
    short_code = scrapy.Field(output_processor=TakeFirst())
    symbol = scrapy.Field(output_processor=TakeFirst())
    category = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(default="", output_processor=TakeFirst())
    content = scrapy.Field(output_processor=Join())  # join the list into a single string, separated by space
    summary = scrapy.Field(output_processor=TakeFirst())
    date = scrapy.Field(output_processor=TakeFirst())
    scraped_date = scrapy.Field(output_processor=TakeFirst())
