# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json



class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'another_province_into_zhejiang'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://115.29.2.37:8080/enterprise_sw.php?p=1'
        self.index = 1
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {}
        self.data['area'] = '浙江省'
        self.data['companyArea'] = ''
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        self.data['contactAddress'] = ''
        self.data['contactMan'] = ''
        self.bigurl = 'http://115.29.2.37:8080/'
        yield scrapy.Request(url=self.url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        tr = Selector(response=response).xpath('//table[@class="t1"]/tr[@class="auto_h"]')
        for t in tr:
            company_name = t.xpath('./td/div/a/@title').extract_first()
            number = t.xpath('./td[3]/text()').extract_first()
            print(self.bigurl + company_name, 'AAAAAAAAAAAAAAAAAAAA')
            print(company_name, number)
            number = number.split()
            if not number:
                self.data['licenseNum'] = ''
            else:
                number = number[0]
                if len(number) != 18:
                    self.data['licenseNum'] = ''
                else:
                    self.data['licenseNum'] = number
            self.data['companyName'] = company_name
            print(self.data)
            yield scrapy.Request(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                method="POST",
                headers={'Content-Type': 'application/json'},
                body=json.dumps(self.data),
                callback=self.zz,
                meta={'company_name': company_name, 'data': self.data},
                dont_filter=True
            )
        self.index = self.index + 1
        if self.index != 285:
            yield scrapy.Request(url='http://115.29.2.37:8080/enterprise_sw.php?p=%s' % self.index, callback=self.parse,
                                 dont_filter=True)

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

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@style="text-align: left"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@width="150"]')[2].xpath('text()').extract_first()
        company_name = company_name.split()[0]
        number = number.split()
        # if number != []:
        #     number = number[0]
        #     if len(number) != 18:
        #         self.data['licenseNum'] = ''
        #     else:
        #         self.data['licenseNum'] = number
        # else:
        #     self.data['licenseNum'] = ''
        # self.data['companyName'] = company_name
        # print(self.data)
        # yield scrapy.Request(
        #     url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
        #     # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
        #     method="POST",
        #     headers={'Content-Type': 'application/json'},
        #     body=json.dumps(self.data),
        #     callback=self.zz,
        #     meta={'company_name': company_name, 'data': self.data},
        #     dont_filter=True
        # )

