# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import re
import json


class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'Liaoning_outside'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://218.60.144.163/LNJGPublisher/corpinfo/CorpInfo.aspx'
        # self.whole_url = 'http://js.shaanxi.gov.cn:9010/SxApp/share/WebSide/EntSafeQuali.aspx?fcol=80001930&fsid=325'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.p_inside = True
        self.p_outside= True
        self.province = 1
        self.data = {}
        self.data['contactMan'] = ''
        self.data['area'] = '辽宁省'
        self.data['companyArea'] = ''
        self.data['contactPhone'] = ''
        self.data['contactAddress'] = ''
        self.data['token'] = self.token
        self.index = 1
        self.bigurl = 'http://218.60.144.163/LNJGPublisher/corpinfo/outCaseCorpDetailInfo.aspx?Fid='
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        __VIEWSTATE = Selector(response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __EVENTTARGET = 'Linkbutton8'
        data = {}
        data['__VIEWSTATE'] = __VIEWSTATE
        data['__EVENTVALIDATION'] = __EVENTVALIDATION
        data['__EVENTTARGET'] = __EVENTTARGET
        visible_province = Selector(response).xpath('//td[@class="align_center"]/a/@onclick')
        print(len(visible_province), 'zzzzzzzzzzzzzzzzzzzzzzzz')
        for v in visible_province:
            company_name = v.extract()
            re_a = 'onshow\(\'(.*)\'\)'
            url_company = re.findall(re_a, company_name)[0]
            print(self.url + url_company, 'zzzzzzzzzzzzzzzzzzzz')
            yield scrapy.Request(url=self.bigurl + url_company, callback=self.company_information)
        self.index = self.index + 1
        if self.province != 138:
            data['newpage'] = str(self.province)
            yield scrapy.FormRequest(url=self.url, callback=self.parse, formdata=data)

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@class="name_level3"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@id="CorpCode"]/text()').extract_first()
        person = Selector(response=response).xpath('//td[@id="Td4"]/text()').extract_first()
        company_name = company_name.split()[0]
        print(number, 'zzzzzzzzzzzzzzzzzzzz')
        self.data['companyName'] = company_name
        if person == None:
            self.data['contactPhone'] = ''
        else:
            person = person.split()[0]
            self.data['contactPhone'] = person
        if number != None:
            number = number.split()[0]
            if len(number) != 18:
                self.data['licenseNum'] = ''
            else:
                self.data['licenseNum'] = number
        else:
            self.data['licenseNum'] = ''
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