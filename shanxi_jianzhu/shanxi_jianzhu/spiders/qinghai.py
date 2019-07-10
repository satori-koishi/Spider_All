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


class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'qinghai'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://jzsc.qhcin.gov.cn/dataservice/query/comp/list'
        self.index = 1
        self.x = 1
        self.flag = True
        self.into = '63'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://jzsc.qhcin.gov.cn'
        yield scrapy.FormRequest(url=self.url, formdata={'comp_zone': self.into}, callback=self.parse)

    def parse(self, response):

        a_href_all = Selector(response=response).xpath('//table[@class="table_box"]/tbody/tr/@onclick')
        print(len(a_href_all))
        for t in a_href_all:
            a_url = t.extract()
            re_a = 'javascript:location.href=\'(.*)\''
            re_a = re.findall(re_a, a_url)[0]
            re_a = self.bigurl + re_a
            yield scrapy.Request(url=re_a, callback=self.company_information)
        self.index = self.index + 1
        send_data = {}
        send_data['$total'] = '1331'
        send_data['$reload'] = '0'
        send_data['$pgsz'] = '100'
        send_data['comp_zone'] = self.into
        if not self.index == 92:
            send_data['$pg'] = str(self.index)
            yield scrapy.FormRequest(url=self.url,
                                     formdata=send_data,
                                     callback=self.parse)

    # type_name
    def type_name(self, company_url):
        if company_url.startswith('http://jzjg.gzjs.gov.cn:8088/gzzhxt/SysWebCenter/WebQYSB/Web_GSDWInfo_New.aspx?'):
            scrapy.FormRequest(url=company_url, callback=self.type_name)
        print(company_url.url)

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
        data = {}
        company_name = Selector(response=response).xpath('//span[@class="user-name"]/text()').extract_first()
        licenseNum = Selector(response=response).xpath('//div[@class="bottom"]/dl[1]/dt/text()').extract_first()
        data['companyName'] = company_name
        data['area'] = ''
        data['companyArea'] = '青海省'
        data['token'] = self.token
        data['contactMan'] = ''
        data['contactAddress'] = ''
        data['contactPhone'] = ''
        if licenseNum != None:
            if len(licenseNum) != 18:
                data['licenseNum'] = ''
            else:
                data['licenseNum'] = licenseNum
        else:
            data['licenseNum'] = ''
        print(data)
        yield scrapy.Request(
            url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
            # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
            method="POST",
            headers={'Content-Type': 'application/json'},
            body=json.dumps(data),
            callback=self.zz,
            meta={'company_name': company_name, 'data': data}
        )
