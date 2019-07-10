# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re


class XinJiangOtherProvince(scrapy.Spider):
    name = 'XinJiangOtherProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.bigurl = 'http://jsy.xjjs.gov.cn'
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://jsy.xjjs.gov.cn/dataservice/query/comp/list'
        self.need_url = 'http://jsy.xjjs.gov.cn:80/pub/query/baComp/baCompList'
        self.flag = True
        self.number = 5
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.index = 1
        self.data = {'licenseNum': '', 'contactMan': '', 'area': '新疆维吾尔自治区', 'companyArea': '', 'contactAddress': '',
                     'contactPhone': '', 'token': self.token}

    def start_requests(self):
        yield scrapy.FormRequest(url=self.url, formdata={'comp_zone': 'XX'},
                                 callback=self.page_transfer)

    def page_transfer(self, response):
        info_page = Selector(response=response).xpath("//a[@sf='pagebar']").extract_first()
        total = 'tt:(\d+),'
        page = 'pc:(\d+),'
        total = re.findall(total, info_page)[0]
        page = re.findall(page, info_page)[0]
        send_data = {'$total': total, '$pgsz': '15', '$reload': '0', 'comp_zone': 'XX', '$pg': page}
        print(total, page, type(total))
        yield scrapy.FormRequest(
            url=self.url,
            callback=self.parse,
            formdata=send_data,
            meta={'page': page, 'total': total}
        )

    def parse(self, response):
        div_under_table = Selector(response).xpath('//tbody/tr/@onclick')
        for d in div_under_table:
            company_name = d.extract()
            re_a = 'javascript:location.href=\'(.*)\''
            company_data = re.findall(re_a, company_name)[0]
            print(company_data, 'aaaaaaaaaaaaaaaaaaaaaaaa')
            yield scrapy.Request(url=self.bigurl + company_data, callback=self.company_information)
        send_data = {'$total': response.meta['total'], '$pgsz': '15', '$reload': '0', 'comp_zone': 'XX'}
        print(response.meta['page'], type(response.meta['page']))
        page = int(response.meta['page'])
        page -= 1
        self.number -= 1
        if page != 0:
            send_data['$pg'] = str(page)
            yield scrapy.FormRequest(url=self.url, formdata=send_data, callback=self.parse,
                                     meta={'page': page, 'total': response.meta['total']}
                                     )

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//span[@class="user-name"]/text()').extract_first()
        number = Selector(response=response).xpath('//div[@class="bottom"]/dl/dt/text()').extract_first()
        company_name = company_name.split()[0]
        repeat = self.r.sadd('Company_name', company_name + '新疆省')
        if repeat:
            if number is not None:
                number = number.split()[0]
                if len(number) != 18:

                    self.data['licenseNum'] = ''
                else:
                    self.data['licenseNum'] = number
            else:
                self.data['licenseNum'] = ''
            self.data['companyName'] = company_name
            print(self.data)
            yield scrapy.Request(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                method="POST",
                headers={'Content-Type': 'application/json'},
                body=json.dumps(self.data),
                callback=self.zz,
                meta={'company_name': company_name,'data':self.data}
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
        if not_company_code == -102 or not_company_code == -118:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')
