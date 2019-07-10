# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re


class HuBeiOtherProvince(scrapy.Spider):
    name = 'HuBeiOtherProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = [{'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=8': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=9': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=10': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=11': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=12': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=13': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=14]': 1}
                    ]
        self.index = 1
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {'companyArea': '', 'area': '湖北省', 'contactPhone': '', 'token': self.token}
        self.bigurl = 'http://59.175.169.110/web/QyManage/'
        self.G = None
        self.b_page = True

    def start_requests(self):
        for i in self.url:
            for v, k in i.items():
                yield scrapy.Request(url=v, callback=self.parse, dont_filter=True, meta={'page': k})

    def parse(self, response):
        post_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        post_data['__VIEWSTATE'] = __VIEWSTATE
        post_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        post_data['__EVENTTARGET'] = 'lbtnNext'
        now_url = response.url
        now_number = 'http://59.175.169.110/web/QyManage/QyList.aspx\?qylx=(\d)'
        zz = re.findall(now_number, now_url)[0]
        post_data['hfQylx'] = zz
        page = Selector(response=response).xpath('//span[@id="labPageCount"]/text()').extract_first()
        now_page = int(page)
        now_page += 1
        all_url = Selector(response=response).xpath('//table[@class="table"]/tr/td/a/@href')
        print('当前一页的长度%s' % len(all_url))
        for a in all_url:
            url = self.bigurl + a.extract()
            yield scrapy.Request(url=url, callback=self.company_information, dont_filter=True)
            # print(a.extract())
        index = int(response.meta['page']) + 1
        if index != now_page:
            post_data['txtPageIndex'] = str(index)
            print('这个网页的地址是%s----这是它的第%s页-----她总共%s页' % (response.url, index, now_page))
            yield scrapy.FormRequest(url=response.url,
                                     formdata=post_data,
                                     callback=self.parse,
                                     meta={'page': index},
                                     dont_filter=True)

    def zz(self, response):
        not_company_code = json.loads(response.text)['code']
        not_search_company_name = response.meta['company_name']
        zz_data = response.meta['data']
        self.r.sadd('all_company_name', not_search_company_name)
        print(response.text)
        data = json.dumps(zz_data, ensure_ascii=False)
        print('接口发送的数据%s' % data)
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@id="QYMC"]/text()').extract_first()
        repeat = self.r.sadd('Company_name', company_name + '湖北省')
        repeat = 1
        if repeat:
            number = Selector(response=response).xpath('//td[@id="ZZJGDM"]/text()').extract_first()
            person = Selector(response=response).xpath('//td[@id="WSCLYWFZR_MC"]/text()').extract_first()
            prvince = Selector(response=response).xpath('//td[@id="XZQHDMDsz"]/text()').extract_first()
            city = Selector(response=response).xpath('//td[@id="XZQHDMQx"]/text()').extract_first()
            if prvince is None or city is None:
                self.data['contactAddress'] = ''
            else:
                address = prvince + city
                self.data['contactAddress'] = address
            if person is None:
                self.data['contactMan'] = ''
            else:
                self.data['contactMan'] = person
            self.data['companyName'] = company_name
            if len(number) == 18:
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
                meta={'company_name': company_name, 'data': self.data},
                dont_filter=True
            )

            person_table = Selector(response=response).xpath('//table[@class="table"]/tr')
            person_data = {'companyName': company_name, 'licenseNum': '', 'area': '湖北省', 'major': '', 'regNum': '',
                           'validTime': '', 'tel': '', 'tokenKey': self.token}
            if len(number) == 18:
                person_data['licenseNum'] = number
            for p in person_table:
                person_data = {'companyName': company_name, 'licenseNum': '', 'area': '湖北省', 'major': '', 'regNum': '',
                               'validTime': '', 'tel': '', 'tokenKey': self.token}
                person_name = p.xpath('./td[2]/text()').extract_first().split()[0]
                sex = p.xpath('./td[3]/text()').extract_first().split()[0]
                id_card = p.xpath('./td[4]/text()').extract_first().split()[0]
                person_data['name'] = person_name
                person_data['sex'] = sex
                person_data['idCard'] = id_card
                more_card = p.xpath('./td[5]/br')

                if more_card:
                    for index in range(len(more_card)):
                        print(person_data, 'AAAAAAAAAAAAAAAAAA')
                        card_type = p.xpath('./td[5]/text()')[index].extract().split()[0]
                        card_number = p.xpath('./td[6]/text()')[index].extract().split()[0]
                        person_data['grade'] = card_type
                        person_data['num'] = card_number
                        yield scrapy.FormRequest(
                            url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                            # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecordEngineer.htm',
                            formdata=person_data,
                            callback=self.person_post,
                            meta={'data': person_data},
                            dont_filter=True
                        )
                else:
                    print(person_data)
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': company_name},
                        dont_filter=True,
                    )
        else:
            print('此公司信息已经存在', company_name)

    def person_post(self, response):
        not_company_code = json.loads(response.text)['code']
        print(response.text)
        if not_company_code == -118 or not_company_code == -102:
            self.r.sadd('title_name1', response.meta['company_name'])
            self.r.sadd('title_name3', response.meta['company_name'])
            print('当前公司不存在已经正在添加')
        else:
            print(response.meta['data']['name'], '添加成功')
