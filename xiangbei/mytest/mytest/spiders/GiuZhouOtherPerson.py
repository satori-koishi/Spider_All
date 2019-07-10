# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re
from scrapy import log


class GiuZhouOtherPerson(scrapy.Spider):
    name = 'GiuZhouOtherPerson'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://42.123.101.210:8088/gzzhxt/SYGS/SYGSGL/SWRQQYGSlist_new.aspx'
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.index = 1
        self.data = {'area': '贵州省', 'companyArea': '', 'contactAddress': '', 'contactPhone': '', 'token': self.token}

        self.bigurl = 'http://dn4.gxzjt.gov.cn:1141/WebInfo/Enterprise/'

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        post_forama_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __EVENTTARGET = 'ctl00$ContentMain$LinkButtonNextPage'
        post_forama_data['__VIEWSTATE'] = __VIEWSTATE
        post_forama_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        post_forama_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        post_forama_data['__EVENTTARGET'] = __EVENTTARGET
        a_href_all = Selector(response=response).xpath('//table[@id="ContentMain_DataList1"]/tr/td/ul/li[1]/a/@onclick')
        all_company_name = Selector(response=response).xpath(
            '//table[@id="ContentMain_DataList1"]/tr/td/ul/li[1]/a/@title')
        for t in range(len(a_href_all)):
            number = a_href_all[t].extract()
            company_name = all_company_name[t].extract()
            repeat = self.r.sadd('Company_name', company_name + '贵州')
            repeat = 1
            if repeat:
                re_url = 'ShowWin\(\'(.*)\',\'(.*)\',\'v\'\);return false;'
                url_data = re.findall(re_url, number)
                company_url = 'http://42.123.101.210:8088/gzzhxt/SysWebCenter/' \
                              'WebQYSB/Web_GSDWInfo_New.aspx?opType=v&GUID=%s&CorpCode=%s' \
                              % (url_data[0][0], url_data[0][1],)
                yield scrapy.Request(url=company_url,
                                     headers={
                                         'Referer': 'http://42.123.101.210:8088/gzzhxt/SYGS/SYGSGL/GCCX_new.aspx'},
                                     callback=self.type_name,
                                     meta={'number': url_data[0][1],
                                           'company_name': company_name,
                                           },

                                     dont_filter=True
                                     )
            else:
                print('此公司信息已经存在', company_name)
        page = Selector(response=response).xpath('//input[@id="ContentMain_HidPageCount"]/@value').extract_first()
        self.index = self.index + 1
        if not self.index == int(page):
            post_forama_data['ctl00$ContentMain$HidIndexPage'] = str(self.index)
            yield scrapy.FormRequest(url=self.url,
                                     formdata=post_forama_data,
                                     callback=self.parse,
                                     dont_filter=True)

    def type_name(self, response):
        type_zz = Selector(response=response).xpath('//input[@id="hid_A_UnitType"]/@value').extract_first()
        yield scrapy.FormRequest(url='http://42.123.101.210:8088/gzzhxt/SysWebCenter/WebQYSB/Web_GSDWInfo_New.aspx',
                                 formdata={'ajaxType': 'GetXM',
                                           'UnitType': type_zz,
                                           'CorpCode': response.meta['number']
                                           },
                                 headers={'Content-Type': ' application/x-www-form-urlencoded; charset=UTF-8'},
                                 callback=self.company_information,
                                 meta={'number': response.meta['number'],
                                       'company_name': response.meta['company_name'],
                                       },
                                 dont_filter=True
                                 )

    def company_information(self, response):
        licenseNum = response.meta['number']
        company_name = response.meta['company_name']
        self.r.sadd('贵州省外企业', company_name)
        self.data['companyName'] = company_name
        self.data['area'] = '贵州省'
        self.data['token'] = self.token
        self.data['contactMan'] = response.text
        if licenseNum is not None:
            if len(licenseNum) != 18:
                self.data['licenseNum'] = ''
            else:
                self.data['licenseNum'] = licenseNum
        else:
            self.data['licenseNum'] = ''
        if response.text is not None:
            self.data['contactMan'] = response.text
        else:
            self.data['contactMan'] = ''
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
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')
