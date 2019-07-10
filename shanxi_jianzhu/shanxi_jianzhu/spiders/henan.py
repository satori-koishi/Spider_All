# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json



class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'henan'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://hngcjs.hnjs.gov.cn/SiKuWeb/QiyeList.aspx?type=qyxx&val='
        # self.url = 'http://61.190.70.122:8003/epoint-mini/rest/function/searchSWQY'
        self.index = 1
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {}
        self.data['area'] = ''
        self.data['companyArea'] = '河南省'
        self.data['contactMan'] = ''
        self.data['contactPhone'] = ''
        self.data['contactAddress'] = ''
        self.data['licenseNum'] = ''
        self.data['token'] = self.token
        self.bigurl = 'http://hngcjs.hnjs.gov.cn'
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        psot_forma_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        psot_forma_data['__VIEWSTATE'] = __VIEWSTATE
        psot_forma_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        psot_forma_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        psot_forma_data['__EVENTTARGET'] = 'AspNetPager2'
        psot_forma_data['CretType'] = '全部企业类别'
        self.index = self.index + 1
        psot_forma_data['__EVENTARGUMENT'] = str(self.index)
        tr = Selector(response=response).xpath('//a[@target="_blank"]/@href')
        print(len(tr))
        for t in tr:
            company_url = t.extract()
            yield scrapy.Request(url=self.bigurl + company_url, callback=self.company_information)
        if not self.index == 1035:
            yield scrapy.FormRequest(url='http://hngcjs.hnjs.gov.cn/SiKuWeb/QiyeList.aspx?type=qyxx&val=',
                                      formdata=psot_forma_data,
                                      callback=self.parse)

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
        company_name = Selector(response=response).xpath('//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label10"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@class="inquiry_intitleb"]')[5]\
            .xpath('./span/text()').extract_first()
        company_name = company_name.split()[0]
        self.data['companyName'] = company_name
        if number is not None:
            number = number.split()[0]
            if len(number) == 18:
                self.data['licenseNum'] = number
        # print(self.data)
        # yield scrapy.Request(
        #     url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
        #     # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
        #     method="POST",
        #     headers={'Content-Type': 'application/json'},
        #     body=json.dumps(self.data),
        #     callback=self.zz,
        #     meta={'company_name': company_name, 'data': self.data}
        # )
        person_zz = Selector(response=response).xpath('//table[@id="GridView2"]')
        print(len(person_zz), 'zzzzzzzzzzzzzzzzzzzzzzz')