# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import re
import json
class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'shanxi'
    start_urls = ['http://jzscyth.shaanxi.gov.cn:7001/PDR/network/informationSearch/informationSearchList?libraryName=enterpriseLibrary&pid1=610000']

    def __init__(self):
        # pass
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.flag = True
        self.index = 1
        self.data = {}
        self.data['licenseNum'] = ''
        self.data['contactMan'] = ''
        self.data['area'] = ''
        self.data['companyArea'] = '陕西省'
        self.data['contactAddress'] = ''
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        self.flag = True
    def parse(self, response):
        # time.sleep(3)
        my_tr = Selector(response).xpath('//table[@id="enterpriseLibraryIsHides"]/tr/td[2]/p/a/@onclick')
        # print(my_tr,'zzzzzzzzzzzzzzzzzzzzz')
        for m in my_tr:
            u = m.extract()
            s = 'vie1\(\'(.*)\',\'(.*)\' ,\'(.*)\',\'\'\)'
            list_z = re.findall(s, u)
            print(list_z[0][1], '----', list_z[0][0], '---', list_z[0][2])
            company_url = 'http://jzscyth.shaanxi.gov.cn:7001/PDR/network/Enterprise/Informations/view?enid=%s&name=%s&org_code=%s&type=' %(list_z[0][1], list_z[0][0], list_z[0][2])
            yield Request(url=company_url, callback=self.company_information, dont_filter=True)
        self.index = self.index + 1
        if self.index != 958:
                url = 'http://jzscyth.shaanxi.gov.cn:7001/PDR/network/informationSearch/informationSearchList?' \
                          'pid1=610000&pageNumber=%s&libraryName=enterpriseLibrary' % self.index
                yield Request(url=url, callback=self.parse,dont_filter=True)

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@colspan="3"]/text()').extract_first()
        number = Selector(response=response).xpath('//table[@class="detailTable"]')[0]\
            .xpath('./tr[2]/td[4]/text()').extract_first()
        company_name = company_name.split()[0]
        number = number.split()
        if number != []:
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
