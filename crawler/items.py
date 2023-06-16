import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


class AlphaStreetItem(scrapy.Item):
    symbol = scrapy.Field(output_processor=TakeFirst())
    category = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    date = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
