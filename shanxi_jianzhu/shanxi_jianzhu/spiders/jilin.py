# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import time
import json


class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'jilin'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        now_time = time.time() * 1000
        now_time = int(now_time)
        reduce_time = now_time - 1000000
        self.url = 'http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SnCorpData&CorpName=&QualiType=&TradeID=&BoundID=&LevelID=&CityNum=&nPageIndex=%s&nPageCount=0&nPageRowsCount=0&nPageSize=%s&_=%s' % (1, 20, now_time)
        self.bigurl = 'http://cx.jlsjsxxw.com/'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.flag = True
        self.index = 1
        self.data = {}
        self.data['area'] = ''
        self.data['companyArea'] = '吉林省'
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        zz = Selector(response=response).xpath('//tr/td[2]/a/@href')
        for z in zz:
            company_name = z.extract()
            company_name = company_name.split(r'\"')[1]
            url = company_name.split('..')[1]
            print(url)
            print(self.bigurl + url)
            yield scrapy.Request(url=self.bigurl + url, callback=self.company_information,dont_filter=True)
        self.index = self.index + 1
        print(self.index != 314, 'zzzzzzzzzzzzzzzzzzzzzzz')
        if self.index != 314:
            yield scrapy.Request(url='http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SnCorpData'
                                     '&CorpName=&QualiType=&TradeID=&BoundID=&LevelID'
                                     '=&CityNum=&nPageIndex=%s&nPageCount=0&nPageR'
                                     'owsCount=0&nPageSize=%s&' % (self.index, 20),
                                 callback=self.parse, dont_filter=True)

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@class="name_level3"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@id="LicenseNum"]/text()').extract_first()
        person = Selector(response=response).xpath('//td[@id="LinkMan"]/text()').extract_first()
        address = Selector(response=response).xpath('//td[@id="Description"]/text()').extract_first()
        company_name = company_name.split()[0]
        number = number.split()
        person = person.split()[0]
        address = address.split()
        if person == None:
            self.data['contactMan'] = ''
        self.data['contactMan'] = person
        if address == None:
            self.data['contactAddress'] = ''
        else:
            address = address[0]
            self.data['contactAddress'] = address
        if number != None:
            number = number[0]
            if len(number) != 18:
                self.data['licenseNum'] = ''
            else:
                self.data['licenseNum'] = number
        else:
            self.data['licenseNum'] = ''
        self.data['companyName'] = company_name
        print(self.data)
        yield scrapy.Request(
            url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
            # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
            method="POST",
            headers={'Content-Type': 'application/json'},
            body=json.dumps(self.data),
            callback=self.zz,
            meta={'company_name': company_name, 'data': self.data}
        )

    def zz(self, response):
        not_company_code = json.loads(response.text)['code']
        not_search_company_name = response.meta['company_name']
        zz_data = response.meta['data']
        self.r.sadd('all_company_name', not_search_company_name)
        print(response.text)
        data = json.dumps(zz_data, ensure_ascii=False)
        print(response.meta['data'], 'aaaaaaaaaaaaaaaaaa')
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')