# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZizhisearchItem(scrapy.Item):
    # define the fields for your item here like:

    # 企业名称
    Enterprise_name = scrapy.Field()
    # 统一社会信用代码/注册号
    Registration_number = scrapy.Field()
    # 法定代表人
    Legal_representative = scrapy.Field()
    # 注册地
    Registered_place = scrapy.Field()




