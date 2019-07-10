# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re


class HeNanOtherProvince(scrapy.Spider):
    name = 'HeNanOtherProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.number = 5
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://hngcjs.hnjs.gov.cn/SiKuWeb/WSRY_List.aspx'
        self.index = 0
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {'area': '河南省', 'companyArea': '', 'contactMan': '', 'contactPhone': '', 'contactAddress': '',
                     'licenseNum': '', 'token': self.token}
        self.bigurl = 'http://hngcjs.hnjs.gov.cn/SiKuWeb/'

    def start_requests(self):

        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        page = Selector(response=response).xpath('//div[@id="AspNetPager2"]/ul/li')[12].xpath(
            './a/text()').extract_first()
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        post_data = {'__VIEWSTATE': __VIEWSTATE, '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                     '__EVENTVALIDATION': __EVENTVALIDATION, '__EVENTTARGET': 'AspNetPager2',
                     '__EVENTARGUMENT': page}
        yield scrapy.FormRequest(url='http://hngcjs.hnjs.gov.cn/SiKuWeb/WSRY_List.aspx',
                                 formdata=post_data,
                                 callback=self.parse,
                                 meta={'page': page}
                                 )

    def parse(self, response):
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        post_data = {'__VIEWSTATE': __VIEWSTATE, '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                           '__EVENTVALIDATION': __EVENTVALIDATION, '__EVENTTARGET': 'AspNetPager2'}
        tr = Selector(response=response).xpath('//a[@target="_blank"]/@href')

        for t in tr:
            company_url = t.extract()
            yield scrapy.Request(url=self.bigurl + company_url, callback=self.company_information)
        print(response.meta['page'], type(response.meta['page']))
        page = int(response.meta['page'])
        page -= 1
        post_data['__EVENTARGUMENT'] = str(page)
        if page != 0:
            yield scrapy.FormRequest(url='http://hngcjs.hnjs.gov.cn/SiKuWeb/WSRY_List.aspx',
                                     formdata=post_data,
                                     callback=self.parse,
                                     meta={'page': page}
                                     )

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label10"]/text()').extract_first()
        number = Selector(response=response).xpath('//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label3"]/text()').extract_first()
        person = Selector(response=response).xpath('//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label5"]/text()').extract_first()
        company_name = company_name.split()[0]
        repeat = self.r.sadd('Company_name', company_name + '河南省')
        if repeat:
            self.data['companyName'] = company_name
            if person is not None:
                person = person.split()[0]
                self.data['contactMan'] = person
            else:
                self.data['contactMan'] = ''
            if number is not None:
                number = number.split()[0]
                if len(number) == 18:
                    self.data['licenseNum'] = number
            yield scrapy.Request(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                method="POST",
                headers={'Content-Type': 'application/json'},
                body=json.dumps(self.data),
                callback=self.zz,
                meta={'company_name': company_name, 'data': self.data}
            )

            person_zz = Selector(response=response).xpath('//table[@id="GridView2"]/tbody/tr')
            person_data = {'companyName': company_name,
                           'licenseNum': number, 'name': '', 'area': '河南省', 'sex': '',
                           'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                           'validTime': '', 'tel': '', 'tokenKey': self.token
                           }
            del person_zz[0]
            if len(person_zz) != 0:
                for p in person_zz:
                    person_info = p.xpath('./td')

                    # 姓名
                    name = person_info[1].xpath('text()').extract_first()
                    if name is not None:
                        person_data['name'] = name

                    # 执业印章号
                    regNum = person_info[2].xpath('text()').extract_first()
                    if regNum is not None:
                        person_data['regNum'] = regNum

                    # 注册编号（非注册人员可不填）
                    num = person_info[3].xpath('text()').extract_first()
                    if num is not None:
                        person_data['num'] = num

                    # 注册编号（非注册人员可不填）
                    validTime = person_info[5].xpath('text()').extract_first()
                    if validTime is not None:
                        try:
                            validTime = validTime.split()[0]
                            person_data['validTime'] = validTime.replace('/', '-')
                        except EOFError:
                            pass
                    print(person_data)
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': company_name},
                        dont_filter=True,
                    )
            else:
                print('对不起----%s----没有人员' % company_name)
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
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')

    def person_post(self, response):
        not_company_code = json.loads(response.text)['code']
        print(response.text, response.meta['company_name'])
        if not_company_code == -118 or not_company_code == -102:
            self.r.sadd('title_name1', response.meta['company_name'])
            self.r.sadd('title_name3', response.meta['company_name'])
            print('当前公司不存在已经正在添加')
        else:
            print(response.meta['data']['name'], '添加成功')