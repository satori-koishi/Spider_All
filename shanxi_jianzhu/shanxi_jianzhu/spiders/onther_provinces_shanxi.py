# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import json

class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'another_province_into_shanxi'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://js.shaanxi.gov.cn:9010/SxApp/share/WebSide/ZZCXSGList.aspx?fsid=180'
        self.shanxi_information = {}
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.flag = True
        self.data = {}
        self.index = 1
        self.data['licenseNum'] = ''
        self.data['contactMan'] = ''
        self.data['area'] = '陕西省'
        self.data['companyArea'] = ''
        self.data['contactAddress'] = ''
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        yield scrapy.Request(url=self.url, callback=self.parse)
    def parse(self, response):
        __VIEWSTATE = Selector(response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response).xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        div_under_table = Selector(response).xpath('//div[@class="ch_Grid"]/table/tr/td[2]/text()')
        for d in div_under_table:
            company_name = d.extract()
            company_name = company_name.split()[0]
            print(company_name)
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
            # self.r.sadd('another_into_shanxi_make', company_name)
        self.index =self.index + 1
        if self.index != 179:
                yield scrapy.FormRequest(url=self.url, callback=self.parse, formdata={'__VIEWSTATE':__VIEWSTATE,
                                                                                              '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                                                                                               '__EVENTVALIDATION': __EVENTVALIDATION,
                                                                                               'Pager1': ' Go',
                                                                                             'Pager1_input':str(self.index)},
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
