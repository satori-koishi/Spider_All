# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import json

class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'another_into_hebei'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.url = 'http://zfcxjst.hebei.gov.cn/was5/web/detail?record=1&channelid=204700'
        self.flag = True
        self.index = 1
        self.data = {}
        self.data['area'] = '河北省'
        self.data['companyArea'] = ''
        self.data['contactAddress'] = ''
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        # print(response.text)
        company_name = Selector(response).xpath('//table[@align="center"]/tr[3]/td[2]/text()').extract_first()
        number = Selector(response).xpath('//table[@align="center"]/tr[4]/td[2]/text()').extract_first()
        self.data['companyName'] = company_name
        if number is not None:
            if len(number) != 18:
                self.data['licenseNum'] = ''
            else:
                self.data['licenseNum'] = number
        else:
            self.data['licenseNum'] = ''
        div_table = Selector(response=response).xpath('//td[@colspan="4"]')[6]
        contactMan = div_table.xpath('text()').extract_first()
        if contactMan is not None:
            self.data['contactMan'] = contactMan
        else:
            self.data['contactMan'] = ''
        print(self.data)
        yield scrapy.FormRequest(url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                  method="POST",
                  headers={'Content-Type': 'application/json'},
                  body=json.dumps(self.data),
                  callback=self.zz,
                  meta={'company_name': company_name,'data':self.data})
        self.index = self.index + 1
        if self.index != 400:
            url = 'http://zfcxjst.hebei.gov.cn/was5/web/detail?record=%s&channelid=204700'% self.index
            yield scrapy.Request(url=url, callback=self.parse)

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