# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import re
import json
import time
class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'Liaoning'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://218.60.144.163/LNJGPublisher/corpinfo/CorpInfo.aspx'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.p_inside = True
        self.p_outside= True
        self.province = 1
        self.data = {}
        self.data['contactMan'] = ''
        self.data['area'] = ''
        self.data['companyArea'] = '辽宁省'
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        yield scrapy.Request(url=self.url, callback=self.parse, dont_filter=True)
    def parse(self, response):
        __VIEWSTATE = Selector(response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __EVENTTARGET = 'Linkbutton3'
        div_under_table = Selector(response).xpath('//div[@class="list_container inner"]')
        data = {}
        data['__VIEWSTATE'] = __VIEWSTATE
        data['hidd_type'] = '1'
        data['__EVENTVALIDATION'] = __EVENTVALIDATION
        data['__EVENTTARGET'] = __EVENTTARGET

        visible_province = div_under_table.xpath('./table/tbody/tr/td[3]/a/@onclick')
        for v in visible_province:
            company_name = v.extract()
            re_data = 'OpenCorpDetail\(\'(.*)\',\'(.*)\',\'(.*)\'\)'
            company_name = re.findall(re_data, company_name)
            rowGuid = company_name[0][0]
            CorpCode = company_name[0][1]
            CorpName = company_name[0][2]
            url = 'http://218.60.144.163/LNJGPublisher/corpinfo/CorpDetailInfo.aspx?rowGuid=%s&CorpCode=%s&CorpName=%s&VType=1' %(rowGuid, CorpCode, CorpName)
            yield scrapy.Request(url=url, callback=self.company_information, dont_filter=True)

        self.province = self.province + 1
        if self.province != 600:
            data['newpage'] = str(self.province)
            yield scrapy.FormRequest(url=self.url, callback=self.parse, formdata=data, dont_filter=True)

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@class="name_level3"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@id="LicenseNum"]/text()').extract_first()
        address = Selector(response=response).xpath('//td[@id="Description"]/text()').extract_first()
        company_name = company_name.split()[0]
        address = address.split()[0]
        self.data['companyName'] = company_name
        if number != None:
            number = number.split()[0]
            if len(number) != 18:
                self.data['licenseNum'] = ''
            else:
                self.data['licenseNum'] = number
        else:
            self.data['licenseNum'] = ''
        if address == None:
            self.data['contactAddress'] = ''
        else:
            self.data['contactAddress'] = address
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
        print(response.meta['data'], 'aaaaaaaaaaaaaaaaaa')
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')
