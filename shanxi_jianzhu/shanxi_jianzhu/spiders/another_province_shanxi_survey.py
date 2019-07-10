# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import random
import re
import json
class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'another_province_into_survey'
    flag = True

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://js.shaanxi.gov.cn:9000/QualiSearch/Ajax/QualiList.ashx'
        zz  = {}
        zz['i'] = '1'
        zz['c'] = '1'
        zz['p'] = '1150'
        zz['s'] = ' and  t1.FId=t3.FBaseInfoId and t1.FIsDeleted=0  and t3.FIsDeleted=0 and t1.FState=2 '
        no_zz = random.random()
        no_zz = str(no_zz)
        zz['e'] = no_zz
        self.data = {}
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data['licenseNum'] = ''
        self.data['contactMan'] = ''
        self.data['area'] = '陕西省'
        self.data['companyArea'] = ''
        self.data['contactAddress'] = ''
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        yield scrapy.FormRequest(url=self.url, callback=self.parse, formdata=zz)

    def parse(self, response):
        # print(response.text)
        div_under_table = Selector(response).xpath('//table/tr/td[2]/a')
        for d in div_under_table:
            company_name = d.xpath('text()').extract_first()
            # self.r.sadd('another_province_into_survey', company_name)
            self.data['companyName'] = company_name
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