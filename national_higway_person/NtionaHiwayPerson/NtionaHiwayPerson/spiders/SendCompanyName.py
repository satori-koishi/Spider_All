# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import redis
import json
import re


class SendCompanyName(scrapy.Spider):
    name = 'SendCompanyName'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://xypt.mwr.gov.cn/UnitCreInfo/listCydwPage.do?'
        pool = redis.ConnectionPool(
            host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.index = 1
        self.flag = True

    def start_requests(self):
        yield scrapy.Request(url=self.url + 'currentPage=1&showCount=20',
                             callback=self.parse,
                             )

    def parse(self, response):
        if self.flag:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[6].xpath('./a/@onclick') \
                .extract_first()
            self.flag = False
        else:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[8].xpath('./a/@onclick') \
                .extract_first()
        page = re.findall('nextPage\((\d+)\)', page)[0]
        page = int(page) + 1
        print(page, 'page')
        person_url = Selector(response=response).xpath('//table[@id="example-advanced"]/tbody/tr')
        for p in person_url:
            zz = p.xpath('./td[2]/a/@href').extract_first()
            unit_type = p.xpath('./td[3]/text()').extract_first()
            if unit_type is None:
                unit_type = ''
            a = re.findall('javascript:toChangeTop\(\'(.*)\'\);toDetail\(\'(.*)\'\)', zz)
            yield scrapy.Request(url='http://xypt.mwr.gov.cn/UnitCreInfo/frontunitInfoList.do?ID=%s&menu=%s'
                                     % (a[0][1], a[0][0]),
                                 callback=self.company_info,
                                 meta={'unit_type': unit_type}
                                 )
        self.index += 1
        if page != self.index:
            yield scrapy.Request(url=self.url + 'currentPage=%s&showCount=20' % self.index,
                                 callback=self.parse,
                                 )

    def company_info(self, response):
        data = {'name': '', 'licenseNum': '', 'url': '', 'email': '', 'tel': '', 'tokenKey': self.token}
        company_name = Selector(response=response).xpath('//td[@colspan="3"]')[0].xpath('./a/@title').extract_first()
        data['name'] = company_name

        yield scrapy.FormRequest(
            url='https://api.maotouin.com/rest/companyInfo/updateCompany.htm',
            formdata=data,
            dont_filter=True,
            meta={'company_name': company_name},
            callback=self.company
        )

    def company(self, response):
        not_company_code = json.loads(response.text)['code']
        print(response.text, response.meta['company_name'])
        if not_company_code == -118 or not_company_code == -102:
            self.r.sadd('NonExistentWaterCompany', response.meta['company_name'])
            print('当前公司不存在已经正在添加')
        else:
            self.r.sadd('OkWaterCompany', response.meta['company_name'])
            print(response.meta['company_name'], '添加成功')

