# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import re
import json

class ShanxiJianzhuImformationSpider(scrapy.Spider):

    name = 'jiangxi'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://59.52.254.106:8093/qualificationCertificateListForPublic'
        self.flag = True
        self.bigurl = 'http://59.52.254.106:8093'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.index = 1
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        div_under_table = Selector(response).xpath('//table [@class="listTable hoverTable trbgTable detailPopupTable"]/tr/td[3]/a/@onclick')
        print(len(div_under_table))
        for d in div_under_table:
            url = d.extract()
            # print(url)
            new_url = re.findall("winopen\('(.*)',1000,500,'详情'\);",url)[0]
            new_url = self.bigurl + new_url
            print(new_url)
            yield scrapy.Request(url=new_url, callback=self.company_information)
        self.index = self.index + 1
        if self.index != 1342:
            url = 'http://59.52.254.106:8093/qualificationCertificateListForPublic?pageIndex=%s' % self.index
            yield scrapy.Request(url=url, callback=self.parse)

    def company_information(self, response):
        # print(response.text)
        tr = Selector(response=response).xpath('//table[@class="addProjectTable siteFrome_info"]/tr')
        # print(tr)
        company_name = tr[0].xpath('./td[2]/text()').extract_first()
        number = tr[3].xpath('./td[2]/text()').extract_first()
        company_name = company_name.split()[0]
        number = number.split()[0]
        print(number)
        data = {}
        data['companyName'] = company_name
        data['licenseNum'] = number
        data['contactMan'] = ''
        data['companyArea'] = '江西省'
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
            meta={'company_name': company_name,'data':data}
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
