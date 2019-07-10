# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import re
import json


class ShanXiProvince(scrapy.Spider):
    name = 'ShanXiProvince'
    start_urls = [
        'http://jzscyth.shaanxi.gov.cn:7001/PDR/network/informationSearch/informationSearchList?libraryName=enterpriseLibrary&pid1=610000']

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.flag = True
        self.index = 1
        self.data = {'licenseNum': '', 'contactMan': '', 'area': '', 'companyArea': '陕西省', 'contactAddress': '',
                     'contactPhone': '', 'token': self.token}

    def parse(self, response):
        my_tr = Selector(response).xpath('//table[@id="enterpriseLibraryIsHides"]/tr/td[2]/p/a/@onclick')
        for m in my_tr:
            u = m.extract()
            s = 'vie1\(\'(.*)\',\'(.*)\' ,\'(.*)\',\'\'\)'
            list_z = re.findall(s, u)
            print(list_z[0][1], '----', list_z[0][0], '---', list_z[0][2])
            company_url = 'http://jzscyth.shaanxi.gov.cn:7001/PDR/network/Enterprise/Informations/view?enid=%s&name=%s&org_code=%s&type=' % (
                list_z[0][1], list_z[0][0], list_z[0][2])
            yield Request(url=company_url, callback=self.company_information, dont_filter=True)
        if self.flag:
            page = Selector(response=response).xpath('//td[@class="page1"]/text()').extract_first()
            xx = '共(\d+)页'
            page = re.findall(xx, page)[0]
            self.flag = False
        else:
            page = int(response.meta['page'])
        self.index = self.index + 1
        if self.index != int(page):
            url = 'http://jzscyth.shaanxi.gov.cn:7001/PDR/network/informationSearch/informationSearchList?' \
                  'pid1=610000&pageNumber=%s&libraryName=enterpriseLibrary' % self.index
            yield Request(url=url, callback=self.parse, dont_filter=True, meta={'page': page})

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@colspan="3"]/text()').extract_first()
        number = Selector(response=response).xpath('//table[@class="detailTable"]')[0] \
            .xpath('./tr[2]/td[4]/text()').extract_first()
        company_name = company_name.split()[0]
        repeat = self.r.sadd('Company_name', company_name)
        if repeat:
            number = number.split()
            if number:
                number = number[0]
                if len(number) != 18:
                    self.data['licenseNum'] = ''
                else:
                    self.data['licenseNum'] = number
            else:
                self.data['licenseNum'] = ''
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
        else:
            print('此公司信息已经存在', company_name)

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
