# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re

class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'another_into_xinjiang'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://jsy.xjjs.gov.cn/dataservice/query/comp/list'
        self.need_url = 'http://jsy.xjjs.gov.cn:80/pub/query/baComp/baCompList'
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {}
        self.index = 1
        self.data['licenseNum'] = ''
        self.data['contactMan'] = ''
        self.data['area'] = '新疆维吾尔自治区'
        self.data['companyArea'] = ''
        self.data['contactAddress'] = ''
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        self.bigurl = 'http://jsy.xjjs.gov.cn'
        yield scrapy.FormRequest(url=self.url, formdata={'comp_zone': 'XX'},
                                 callback=self.parse)

    def parse(self, response):
        div_under_table = Selector(response).xpath('//tbody/tr/@onclick')
        # print(div_under_table)
        # print(len(div_under_table))
        for d in div_under_table:
            company_name = d.extract()
            re_a = 'javascript:location.href=\'(.*)\''
            company_data = re.findall(re_a, company_name)[0]
            print(company_data)
            yield scrapy.Request(url=self.bigurl + company_data, callback=self.company_information)
        #     self.r.sadd('another_into_xinjiang', company_name)
        send_data = {}
        send_data['$total'] = '3748'
        send_data['$pgsz'] = '15'
        send_data['$reload'] = '0'
        send_data['comp_zone'] = 'XX'
        self.index = self.index + 1
        if self.index != 270:
            send_data['$pg'] = str(self.index)
            yield scrapy.FormRequest(url=self.url, formdata=send_data, callback=self.parse)

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//span[@class="user-name"]/text()').extract_first()
        number = Selector(response=response).xpath('//div[@class="bottom"]/dl/dt/text()').extract_first()
        company_name = company_name.split()[0]
        if number != None:
            number = number.split()[0]
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
            meta={'company_name': company_name,'data':self.data}
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
