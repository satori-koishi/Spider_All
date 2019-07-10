# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import json
class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'hebei'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.url = 'http://zfcxjst.hebei.gov.cn/was5/web/search?page=1&channelid=247697&perpage=100&outlinepage=10'
        self.flag = True
        self.data = {}
        self.data['licenseNum'] = ''
        self.data['contactMan'] = ''
        self.data['area'] = ''
        self.data['companyArea'] = '河北省'
        self.data['contactAddress'] = ''
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        # print(response.text)
        div_under_table = Selector(response).xpath('//div[@class="tabbox"]/table/tr/td[3]/text()')
        del div_under_table[0]
        print(len(div_under_table))
        for d in div_under_table:
            company_name = d.extract()
            self.data['companyName'] = company_name
            print(self.data, '发送全部数据')
            yield Request(
                  url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                  # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                  method="POST",
                  headers={'Content-Type': 'application/json'},
                  body=json.dumps(self.data),
                  callback=self.zz,
                  meta={'company_name': company_name, 'data': self.data}
                          )
                # self.r.sadd('hebei', company_name)
        if self.flag:
            for p in range(1, 174):
                if p == 173:
                    self.flag = False
                url = 'http://zfcxjst.hebei.gov.cn/was5/web/search?page=%s&channelid=247697&perpage=100&outlinepage=10'% p
                yield scrapy.Request(url=url, callback=self.parse)

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