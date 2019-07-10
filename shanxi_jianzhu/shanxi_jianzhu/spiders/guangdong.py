# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json

class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'guangdong'

    def start_requests(self):
        # pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        # self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://113.108.219.52/Dop/Open/EnterpriseList.aspx'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.flag = True
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        tr = Selector(response=response).xpath('//table[@class="data-list"]/tr')
        del tr[0]
        data = {}
        data['contactMan'] = ''
        data['companyArea'] = '广东省'
        data['area'] = ''
        data['contactAddress'] = ''
        data['contactMan'] = ''
        data['contactPhone'] = ''
        data['token'] = self.token
        for t in tr:
            companyName = t.xpath('./td[1]/a/text()').extract_first()
            data['companyName'] = companyName
            licenseNum = t.xpath('./td[3]/text()').extract_first()
            data['licenseNum'] = licenseNum
            print(data)
            yield Request(url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                           method="POST",
                           headers={'Content-Type': 'application/json'},
                           body=json.dumps(data),
                           callback=self.zz
                           )

    def zz(self,response):
        print(response.text)


