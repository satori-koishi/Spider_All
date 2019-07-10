# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re


class HuJianOtherZhaoBiao(scrapy.Spider):
    name = 'HuJianOtherZhaoBiao'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.index = 5
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/CompanyQuery.aspx?bussinessSystemID=42'
        self.x = 1
        self.x = True
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/'

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        post_forama_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        post_forama_data['__VIEWSTATE'] = __VIEWSTATE
        post_forama_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        post_forama_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        if self.x:
            post_forama_data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder$pGrid$lastpagebtn'
            self.x = False
        else:
            post_forama_data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder$pGrid$prepagebtn'
        post_forama_data['ctl00$ContentPlaceHolder$ddlBussinessSystem'] = '42'

        tr = Selector(response=response).xpath('//table[@id="ctl00_ContentPlaceHolder_gvDemandCompany"]/tr/td/a/@href')
        for t in tr:
            tip = t.extract()
            print(self.bigurl+tip)
            yield scrapy.Request(url=self.bigurl+tip, callback=self.company_information,
                                 dont_filter=True)

        if self.flag:
            page = Selector(response=response).xpath(
                "//td[@style='padding-right:15px;padding-bottom:0px;']/text()").extract_first()
            cc = '第\d+/(.*)页'
            page = re.findall(cc, page)[0]
            self.flag = False
        else:
            page = response.meta['page']
        page = int(page) - 1
        if page != 0:
            yield scrapy.FormRequest(url=self.url,
                                     formdata=post_forama_data,
                                     callback=self.parse,
                                     dont_filter=True,
                                     meta={'page': page}
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

    def company_information(self, response):
        td = Selector(response=response).xpath('//table[@class="form orange"]/tr')
        data = {}
        company_name = td[0].xpath('./td/text()').extract_first()
        company_name = company_name.split()[0]
        repeat = self.r.sadd('Company_name', company_name + '福建省')
        if repeat:
            licenseNum = td[3].xpath('./td[3]/text()').extract_first()
            licenseNum = licenseNum.split()
            if not licenseNum:
                data['licenseNum'] = ''
            else:
                print(licenseNum)
                licenseNum = licenseNum[0]
                if len(licenseNum) == 18:
                    data['licenseNum'] = licenseNum
                else:
                    data['licenseNum'] = ''
            data['companyName'] = company_name
            data['contactMan'] = ''
            data['companyArea'] = ''
            data['area'] = '福建省'
            data['contactAddress'] = ''
            data['contactMan'] = ''
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
        else:
            print('此公司信息已经存在', company_name)
        #


