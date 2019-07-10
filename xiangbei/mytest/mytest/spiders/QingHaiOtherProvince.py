# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re


class QingHaiOtherProvince(scrapy.Spider):
    name = 'QingHaiOtherProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://jzsc.qhcin.gov.cn/dataservice/query/comp/list'
        self.index = 1
        self.flag = True
        self.into = 'XX'
        self.number = 5
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://jzsc.qhcin.gov.cn'

    def start_requests(self):
        yield scrapy.FormRequest(url=self.url, formdata={'comp_zone': self.into}, callback=self.page_transfer)

    def page_transfer(self, response):
        info_page = Selector(response=response).xpath("//a[@sf='pagebar']").extract_first()
        total = 'tt:(\d+),'
        page = 'pc:(\d+),'
        total = re.findall(total, info_page)[0]
        page = re.findall(page, info_page)[0]
        send_data = {'$total': total, '$pgsz': '15', '$reload': '0', 'comp_zone': self.into, '$pg': page}
        print(total, page, type(total))
        yield scrapy.FormRequest(
            url=self.url,
            callback=self.parse,
            formdata=send_data,
            meta={'page': page, 'total': total}
        )

    def parse(self, response):

        a_href_all = Selector(response=response).xpath('//table[@class="table_box"]/tbody/tr/@onclick')
        print(len(a_href_all))
        for t in a_href_all:
            a_url = t.extract()
            re_a = 'javascript:location.href=\'(.*)\''
            re_a = re.findall(re_a, a_url)[0]
            re_a = self.bigurl + re_a
            yield scrapy.Request(url=re_a, callback=self.company_information)
        send_data = {'$total': response.meta['total'], '$reload': '0', '$pgsz': '15', 'comp_zone': self.into}
        print(response.meta['page'], type(response.meta['page']))
        page = int(response.meta['page'])
        page -= 1
        self.number -= 1
        if page != 0:
            send_data['$pg'] = str(page)
            yield scrapy.FormRequest(url=self.url, formdata=send_data, callback=self.parse,
                                     meta={'page': page, 'total': response.meta['total']}
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

    def company_information(self, response):
        data = {}
        company_name = Selector(response=response).xpath('//span[@class="user-name"]/text()').extract_first()
        repeat = self.r.sadd('Company_name', company_name + '青海省')
        if repeat:
            licenseNum = Selector(response=response).xpath('//div[@class="bottom"]/dl[1]/dt/text()').extract_first()
            data['companyName'] = company_name
            data['area'] = '青海省'
            data['companyArea'] = ''
            data['token'] = self.token
            data['contactMan'] = ''
            data['contactAddress'] = ''
            data['contactPhone'] = ''
            if licenseNum is not None:
                if len(licenseNum) != 18:
                    data['licenseNum'] = ''
                else:
                    data['licenseNum'] = licenseNum
            else:
                data['licenseNum'] = ''
            print(data)
            yield scrapy.Request(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                method="POST",
                headers={'Content-Type': 'application/json'},
                body=json.dumps(data),
                callback=self.zz,
                meta={'company_name': company_name, 'data': data}
            )
        else:
            print('此公司信息已经存在', company_name)

