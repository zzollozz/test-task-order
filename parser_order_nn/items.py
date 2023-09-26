# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ParserOrderNnItem(scrapy.Item):
    product_name = scrapy.Field(serializer=str)
    product_price = scrapy.Field(serializer=float)
    product_description = scrapy.Field(serializer=str)
    product_characteristic_key = scrapy.Field()
    product_characteristic_value = scrapy.Field()
    product_characteristic = scrapy.Field(serializer=dict)

