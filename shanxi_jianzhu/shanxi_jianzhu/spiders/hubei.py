# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json



class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'hubei'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://jg.hbcic.net.cn/Ewmwz/QyManage/QyzzSearch.aspx?ssl=107'
        self.index = 1
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        yield scrapy.Request(url=self.url, callback=self.parse,dont_filter=True)

    def parse(self, response):
        psot_forma_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        psot_forma_data['__VIEWSTATE'] = __VIEWSTATE
        psot_forma_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        psot_forma_data['__EVENTTARGET'] = 'lbtnNext'
        psot_forma_data['hSsl'] = '107'
        tr = Selector(response=response).xpath('//table[@class="table"]/tr')
        data = {}
        del tr[0]
        for t in tr:
            company_name = t.xpath('./td[@align="left"]/a/text()').extract_first()
            if company_name == None:
                continue
            company_name = company_name.split()[0]
            print(company_name)
            licenseNum = t.xpath('./td[3]/text()').extract_first()
            if licenseNum !=None:
                licenseNum = licenseNum.split()[0]
                print(licenseNum)
                if len(licenseNum) == 18:
                    data['licenseNum'] = licenseNum
                else:
                    data['licenseNum'] = ''
            else:
                data['licenseNum'] = ''
            data['companyName'] = company_name
            data['companyArea'] = '湖北省'
            data['area'] = ''
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
                )
        self.index = self.index + 1
        if not self.index == 1608:
            yield scrapy.FormRequest(url=self.url,
                                      formdata=psot_forma_data,
                                      callback=self.parse,
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