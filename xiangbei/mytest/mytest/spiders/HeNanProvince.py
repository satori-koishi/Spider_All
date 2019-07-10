# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json


class HeNanProvince(scrapy.Spider):
    name = 'HeNanProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.bigurl = 'http://hngcjs.hnjs.gov.cn'
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://hngcjs.hnjs.gov.cn/SiKuWeb/QiyeList.aspx?type=qyxx&val='
        self.index = 1
        self.flag = True
        self.number = 5
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {'area': '', 'companyArea': '河南省', 'contactMan': '', 'contactPhone': '', 'contactAddress': '',
                     'licenseNum': '', 'token': self.token}

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        page = Selector(response=response).xpath('//div[@id="AspNetPager2"]/ul/li')[12].xpath(
            './a/text()').extract_first()
        print(page, 'AAAAAAAAAA')
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        post_data = {'__VIEWSTATE': __VIEWSTATE, '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                     '__EVENTVALIDATION': __EVENTVALIDATION, '__EVENTTARGET': 'AspNetPager2', 'CretType': '全部企业类别',
                     '__EVENTARGUMENT': page}
        yield scrapy.FormRequest(url='http://hngcjs.hnjs.gov.cn/SiKuWeb/QiyeList.aspx?type=qyxx&val=',
                                 formdata=post_data,
                                 callback=self.parse,
                                 meta={'page': page}
                                 )

    def parse(self, response):
        post_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        post_data['__VIEWSTATE'] = __VIEWSTATE
        post_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        post_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        post_data['__EVENTTARGET'] = 'AspNetPager2'
        post_data['CretType'] = '全部企业类别'
        tr = Selector(response=response).xpath('//a[@target="_blank"]/@href')
        for t in tr:
            company_url = t.extract()
            yield scrapy.Request(url=self.bigurl + company_url, callback=self.company_information)
        page = int(response.meta['page'])
        page -= 1
        post_data['__EVENTARGUMENT'] = str(page)
        self.number -= 1
        if page != 0:
            yield scrapy.FormRequest(url='http://hngcjs.hnjs.gov.cn/SiKuWeb/QiyeList.aspx?type=qyxx&val=',
                                     formdata=post_data,
                                     callback=self.parse,
                                     meta={'page': page}
                                     )

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

    def company_information(self, response):
        company_name = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label10"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@class="inquiry_intitleb"]')[5] \
            .xpath('./span/text()').extract_first()
        company_name = company_name.split()[0]
        repeat = self.r.sadd('Company_name', company_name)
        if repeat:
            self.data['companyName'] = company_name
            if number is not None:
                number = number.split()[0]
                if len(number) == 18:
                    self.data['licenseNum'] = number
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
            person_zz = Selector(response=response).xpath('//table[@id="GridView2"]')
            print(len(person_zz), 'zzzzzzzzzzzzzzzzzzzzzzz')
        else:
            print('此公司信息已经存在', company_name)
