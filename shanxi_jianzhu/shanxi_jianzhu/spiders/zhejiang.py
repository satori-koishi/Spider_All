# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json



class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'zhejiang'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://115.29.2.37:8080/enterprise_ajax.php'
        self.index = 1
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.company_url = 'http://115.29.2.37:8080/'
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        psot_forma_data = {}
        topage = Selector(response=response).xpath('//div[@id="pagebar"]/ul/li[3]/@alt').extract_first()
        psot_forma_data['page'] = topage
        tr = Selector(response=response).xpath('//table[@class="t1"]/tr')
        print(len(tr))
        del tr[0]
        print(len(tr))
        for t in tr:
            td = t.xpath('./td')
            url = td[1].xpath('./div/a/@href').extract_first()
            url = self.company_url + url
            print(url, 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
            yield Request(url=url, callback=self.company_information,
                          dont_filter=True,
                          )
        page = Selector(response=response).xpath('//div[@id="pagebar"]/ul/li[3]/@alt').extract_first()
        self.index = self.index + 1
        if not self.index == 1188:
            yield scrapy.FormRequest(url=self.url,
                                      formdata={'page': page},
                                      callback=self.parse,
                                     dont_filter=True)

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@colspan="5"]/text()')[0].extract()
        address = Selector(response=response).xpath('//td[@colspan="5"]/text()')[1].extract()
        number = Selector(response=response).xpath('//div[@class="detail_list"]/table/tr[2]/td[6]/text()').extract_first()
        person_name = Selector(response=response).xpath('//div[@class="detail_list"]/table/tr[7]/td[2]/text()').extract_first()
        print(company_name, address, number, person_name, 'AAAAAAAAAAAAAAAAAAAAAA')
        data = {}
        print()
        data['companyName'] = company_name
        number = number.split()
        if number != []:
            number = number[0]
            if len(number) == 18:
                data['licenseNum'] = number
            else:
                data['licenseNum'] = ''
        else:
            data['licenseNum'] = ''
        person_name = person_name.split()
        print(person_name, type(person_name), 'AAAAAAAAAAAAAAAAAAAA')
        if person_name != []:
            person_name = person_name[0]
            print(person_name)
            data['contactMan'] = person_name
        else:
            data['contactMan'] = ''
        if address != None:
            adderss = address.split()[0]
            data['contactAddress'] = adderss
        else:
            data['contactAddress'] = ''
        data['companyArea'] = '浙江省'
        data['area'] = ''
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
            meta={'company_name': company_name, 'data': data},
            dont_filter=True
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


