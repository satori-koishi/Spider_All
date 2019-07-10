# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random

class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'anhui'

    def start_requests(self):
        # pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        # self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://hngcjs.hnjs.gov.cn/SiKuWeb/QiyeList.aspx?type=qyxx&val='
        # self.url = 'http://61.190.70.122:8003/epoint-mini/rest/function/searchSWQY'

        self.flag = True
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        print(response.text)
