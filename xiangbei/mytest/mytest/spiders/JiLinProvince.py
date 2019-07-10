# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import time
import json
import re


class JiLinProvince(scrapy.Spider):
    name = 'JiLinProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        now_time = time.time() * 1000
        now_time = int(now_time)
        reduce_time = now_time - 1000000
        self.url = 'http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SnCorpData&CorpName=&QualiType=&TradeID=&BoundID=&LevelID=&CityNum=&nPageIndex=%s&nPageCount=0&nPageRowsCount=0&nPageSize=%s&_=%s' % (
            1, 20, reduce_time)
        self.bigurl = 'http://cx.jlsjsxxw.com/'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.flag = True
        self.index = 1
        self.number = 5
        self.data = {'area': '', 'companyArea': '吉林省', 'contactPhone': '', 'token': self.token}
        self.r = redis.Redis(connection_pool=pool)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        page = json.loads(response.text)['nPageCount']
        print(page, type(page))
        yield scrapy.Request(
            url='http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SnCorpData'
                '&CorpName=&QualiType=&TradeID=&BoundID=&LevelID'
                '=&CityNum=&nPageIndex=%s&nPageCount=0&nPageR'
                'owsCount=0&nPageSize=%s&' % (int(page), 20),
            callback=self.parse,
            meta={'page': int(page)}
        )

    def parse(self, response):
        zz = Selector(response=response).xpath('//tr/td[2]/a/@href')
        for z in zz:
            company_name = z.extract()
            company_name = company_name.split(r'\"')[1]
            url = company_name.split('..')[1]
            yield scrapy.Request(url=self.bigurl + url, callback=self.company_information, dont_filter=True)
        page = int(response.meta['page'])
        page -= 1
        self.number -= 1
        if page != 0:
            yield scrapy.Request(url='http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SnCorpData'
                                     '&CorpName=&QualiType=&TradeID=&BoundID=&LevelID'
                                     '=&CityNum=&nPageIndex=%s&nPageCount=0&nPageR'
                                     'owsCount=0&nPageSize=%s&' % (page, 20),
                                 callback=self.parse, dont_filter=True,
                                 meta={'page': page}
                                 )

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@class="name_level3"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@id="LicenseNum"]/text()').extract_first()
        person = Selector(response=response).xpath('//td[@id="LinkMan"]/text()').extract_first()
        address = Selector(response=response).xpath('//td[@id="Description"]/text()').extract_first()
        company_name = company_name.split()[0]
        repeat = self.r.sadd('Company_name', company_name)
        if repeat:
            number = number.split()
            person = person.split()[0]
            address = address.split()
            if person is None:
                self.data['contactMan'] = ''
            self.data['contactMan'] = person
            if address is None:
                self.data['contactAddress'] = ''
            else:
                address = address[0]
                self.data['contactAddress'] = address
            if number is not None:
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
        else:
            print('此公司信息已经存在', company_name)

    def zz(self, response):
        not_company_code = json.loads(response.text)['code']
        not_search_company_name = response.meta['company_name']
        zz_data = response.meta['data']
        self.r.sadd('all_company_name', not_search_company_name)
        print(response.text)
        data = json.dumps(zz_data, ensure_ascii=False)
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')
