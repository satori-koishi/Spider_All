# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MytestItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


import redis

pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
r = redis.Redis(connection_pool=pool)
repeat = r.scard('person')
print(repeat)
