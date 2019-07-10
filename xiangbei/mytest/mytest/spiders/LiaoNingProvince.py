# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import re
import json
import time


class LiaoNingProvince(scrapy.Spider):
    name = 'LiaoNingProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.url = 'http://218.60.144.163/LNJGPublisher/corpinfo/CorpInfo.aspx'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.province = 1
        self.number = 5
        self.data = {'contactMan': '', 'area': '', 'companyArea': '辽宁省', 'contactPhone': '', 'token': self.token}
        self.r = redis.Redis(connection_pool=pool)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer, dont_filter=True)

    def page_transfer(self, response):
        __VIEWSTATE = Selector(response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __EVENTTARGET = 'Linkbutton4'
        data = {'__VIEWSTATE': __VIEWSTATE, 'hidd_type': '1', '__EVENTVALIDATION': __EVENTVALIDATION,
                '__EVENTTARGET': __EVENTTARGET}
        page = Selector(response=response).xpath('//span[@id="lblPageCount"]/text()').extract_first()
        data['newpage'] = page
        yield scrapy.FormRequest(
            url='http://218.60.144.163/LNJGPublisher/corpinfo/CorpInfo.aspx',
            callback=self.parse,
            formdata=data,
            meta={'page': int(page)}
        )

    def parse(self, response):
        __VIEWSTATE = Selector(response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __EVENTTARGET = 'Linkbutton2'
        div_under_table = Selector(response).xpath('//div[@class="list_container inner"]')
        data = {'__VIEWSTATE': __VIEWSTATE, 'hidd_type': '1', '__EVENTVALIDATION': __EVENTVALIDATION,
                '__EVENTTARGET': __EVENTTARGET}

        visible_province = div_under_table.xpath('./table/tbody/tr/td[3]/a/@onclick')
        print(len(visible_province), 'AAAAAAAAAAAAAAAAAAAAAAAAAAA')
        for v in visible_province:
            company_name = v.extract()
            re_data = 'OpenCorpDetail\(\'(.*)\',\'(.*)\',\'(.*)\'\)'
            company_name = re.findall(re_data, company_name)
            rowGuid = company_name[0][0]
            CorpCode = company_name[0][1]
            CorpName = company_name[0][2]
            repeat = self.r.sadd('Company_name', CorpName)
            if repeat:
                url = 'http://218.60.144.163/LNJGPublisher/corpinfo/' \
                      'CorpDetailInfo.aspx?rowGuid=%s&CorpCode=%s&' \
                      'CorpName=%s&VType=1' % (rowGuid, CorpCode, CorpName)
                yield scrapy.Request(url=url, callback=self.company_information, dont_filter=True)
            else:
                print('此公司信息已经存在', CorpName)

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
        print(response.xpath('//span[@id="lblPageIndex"]').extract_first())
        company_name = Selector(response=response).xpath('//td[@class="name_level3"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@id="LicenseNum"]/text()').extract_first()
        address = Selector(response=response).xpath('//td[@id="Description"]/text()').extract_first()
        company_name = company_name.split()[0]
        address = address.split()[0]
        self.data['companyName'] = company_name
        if number is not None:
            number = number.split()[0]
            if len(number) != 18:
                self.data['licenseNum'] = ''
            else:
                self.data['licenseNum'] = number
        else:
            self.data['licenseNum'] = ''
        if address is None:
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
