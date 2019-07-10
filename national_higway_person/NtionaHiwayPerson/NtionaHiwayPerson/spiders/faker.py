# -*- coding: utf-8 -*-
import scrapy


class FakerSpider(scrapy.Spider):
    name = 'faker'
    # allowed_domains = ['tianyancha.com']
    start_urls = ['http://tianyancha.com/']

    def parse(self, response):
        pass
