# -*- coding: utf-8 -*-
import scrapy
from scrapy import  Selector
# from ..items import ZizhisearchItem
from scrapy.http import Request
class ZizhiseeSpider(scrapy.Spider):
    name = 'zizhisee'
    # allowed_domains = ['zihzitong']
    start_urls = ['http://www.zhujianpt.com/company/0-0-0-0-10.html']

    def parse(self, response):
        # content = str(response.body, encoding='utf-8')
        content = Selector(response=response).xpath('//ul[@class="company_contents"]/li')
        print(content)
        # for i in content:
        #     # 企业名称
        #     name = i.xpath('./div[@class="name left"]/a[@target="_blank"]/text()').extract_first()
        #     # 详细内容url
        #     detailed_url = i.xpath('./div[@class="name left"]/a[@target="_blank"]/@href').extract_first()
        #     # 统一社会信用代码/注册号
        #     number = i.xpath('./div[@class="term left"]/text()').extract_first()
        #     # 法定代表人
        #     person = i.xpath('./div[@class="legal_person left"]/text()').extract_first()
        #     # 注册属地
        #     address = i.xpath('./div[@class="build_area left"]/text()').extract_first()
        #     # data =  ZizhisearchItem()
        #
        #     print(detailed_url)
        #     yield ZizhisearchItem(Enterprise_name=name,Registration_number=number,Legal_representative=person,Registered_place=address)
        # print(content.xpath('div[@class="pagination"]/a/text()').extract_first())
        number = Selector(response=response).xpath('//ul[@class="pagination"]/a/text()')
        page_url = Selector(response=response).xpath('//ul[@class="pagination"]/a/@href')
        print(number,page_url)





