# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import re
import json


class LiaoNingOtherProvince(scrapy.Spider):
    name = 'LiaoNingOtherProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://218.60.144.163/LNJGPublisher/corpinfo/CorpInfo.aspx'
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.number = 5
        self.data = {'contactMan': '', 'area': '辽宁省', 'companyArea': '', 'contactPhone': '', 'contactAddress': '',
                     'token': self.token}
        self.bigurl = 'http://218.60.144.163/LNJGPublisher/corpinfo/outCaseCorpDetailInfo.aspx?Fid='

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        __VIEWSTATE = Selector(response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __EVENTTARGET = 'Linkbutton9'
        data = {'__VIEWSTATE': __VIEWSTATE, 'hidd_type': '2', '__EVENTVALIDATION': __EVENTVALIDATION,
                '__EVENTTARGET': __EVENTTARGET}
        page = Selector(response=response).xpath('//span[@id="lblPageCount1"]/text()').extract_first()
        data['newpage'] = page
        yield scrapy.FormRequest(
            url='http://218.60.144.163/LNJGPublisher/corpinfo/CorpInfo.aspx',
            callback=self.parse,
            formdata=data,
            meta={'page': int(page)}
        )

    def parse(self, response):
        print(response.xpath('//span[@id="lblPageIndex1"]').extract_first())
        __VIEWSTATE = Selector(response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __EVENTTARGET = 'Linkbutton7'
        data = {'__VIEWSTATE': __VIEWSTATE, '__EVENTVALIDATION': __EVENTVALIDATION, '__EVENTTARGET': __EVENTTARGET}
        visible_province = Selector(response).xpath('//td[@class="align_center"]/a/@onclick')
        for v in visible_province:
            company_name = v.extract()
            re_a = 'onshow\(\'(.*)\'\)'
            url_company = re.findall(re_a, company_name)[0]
            yield scrapy.Request(url=self.bigurl + url_company, callback=self.company_information)
        print(response.meta['page'], type(response.meta['page']))
        page = int(response.meta['page'])
        page -= 1
        self.number -= 1
        if page != 0:
            data['newpage'] = str(page)
            yield scrapy.FormRequest(url=self.url, callback=self.parse, formdata=data, dont_filter=True,
                                     meta={'page': page}
                                     )

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@class="name_level3"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@id="CorpCode"]/text()').extract_first()
        person = Selector(response=response).xpath('//td[@id="Td4"]/text()').extract_first()
        company_name = company_name.split()[0]
        repeat = self.r.sadd('Company_name', company_name + '辽宁省')
        if repeat:
            self.data['companyName'] = company_name
            if person is None:
                self.data['contactPhone'] = ''
            else:
                person = person.split()[0]
                self.data['contactPhone'] = person
            if number is not None:
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
        else:
            print('此公司信息已经存在', company_name)

    def zz(self, response):
        not_company_code = json.loads(response.text)['code']
        not_search_company_name = response.meta['company_name']
        zz_data = response.meta['data']
        self.r.sadd('all_company_name', not_search_company_name)
        print(response.text)
        data = json.dumps(zz_data, ensure_ascii=False)
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')