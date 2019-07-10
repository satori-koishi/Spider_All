# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json


class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'fujian'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/CompanyQuery.aspx?bussinessSystemID=39'
        self.index = 1
        self.x = 1
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/'
        yield scrapy.Request(url=self.url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        post_forama_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        post_forama_data['__VIEWSTATE'] = __VIEWSTATE
        post_forama_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        post_forama_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        post_forama_data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder$pGrid$nextpagebtn'
        post_forama_data['ctl00$ContentPlaceHolder$ddlBussinessSystem'] = '39'

        tr = Selector(response=response).xpath('//table[@id="ctl00_ContentPlaceHolder_gvDemandCompany"]/tr/td/a/@href')
        for t in tr:
            tip = t.extract()
            print(self.bigurl + tip)
            yield scrapy.Request(url=self.bigurl + tip, callback=self.company_information, dont_filter=True)

        #                )
        self.index = self.index + 1
        if not self.index == 1430:
            yield scrapy.FormRequest(url=self.url,
                                     formdata=post_forama_data,
                                     callback=self.parse, dont_filter=True)

    def company_information(self, response):
        td = Selector(response=response).xpath('//table[@class="form orange"]/tr')
        data = {}
        company_name = td[0].xpath('./td/text()').extract_first()
        company_name = company_name.split()[0]
        licenseNum = td[3].xpath('./td[3]/text()').extract_first()
        if licenseNum is None:
            data['licenseNum'] = ''
        else:
            licenseNum = licenseNum.split()
            if licenseNum:
                licenseNum = licenseNum[0]
                if len(licenseNum) == 18:
                    data['licenseNum'] = licenseNum
                else:
                    data['licenseNum'] = ''
            else:
                data['licenseNum'] = ''
        data['companyName'] = company_name
        data['contactMan'] = ''
        data['companyArea'] = '福建省'
        data['area'] = ''
        data['contactAddress'] = ''
        data['contactPhone'] = ''
        data['token'] = self.token
        print(data)
        yield scrapy.Request(
            url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
            # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
            method="POST",
            headers={'Content-Type': 'application/json'},
            body=json.dumps(data),
            callback=self.zz,
            meta={'company_name': company_name, 'data': data},
            dont_filter=True
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
