# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GithubcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    url = scrapy.Field()
    about = scrapy.Field()
    last_updated = scrapy.Field()
    languages = scrapy.Field()
    commits = scrapy.Field()

    
    pass
