# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
from scrapy.http import Request
from ..items import ZizhinameItem

class ZixinSpider(scrapy.Spider):
    name = 'zixin'
    # allowed_domains = ['www.zhujianpt.com/company']
    start_urls = ['https://www.zhujianpt.com/company/0-1631-0-0-1.html']
    # 去重
    all_url = set()
    # 获取建筑网信息
    def parse(self, response):
        """爬去建筑网所有公司名称"""
        content = Selector(response=response).xpath('//ul[@class="company_contents"]/li')
        for i in content:
            name = i.xpath('./div[@class="name left"]/a[@target="_blank"]/text()').extract_first()
            print('----', name)
            yield ZizhinameItem(name=name)
        page_url = Selector(response=response).xpath('//div[@class="pagination"]/a[re:test(@href,"company/0-1631-0-0-\d.html")]')
        for p in page_url:
            if not p.xpath('@href').extract_first() in self.all_url:
                self.all_url.add(p.xpath('@href').extract_first())
                url = 'https://www.zhujianpt.com' + p.xpath('@href').extract_first()
                yield Request(url)




