# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re


class XiZangProvinceMax(scrapy.Spider):
    name = 'XiZangProvinceMax'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.index = 1
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://111.11.196.111/aspx/corpinfo/CorpInfo.aspx?corpname=&cert=&PageIndex=1'
        self.flag = True
        self.into = 'XX'
        self.number = 5
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://111.11.196.111'

    def start_requests(self):

        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        page = Selector(response=response).xpath('//span[@id="pagecountCtrl"]/text()').extract_first()
        yield scrapy.Request(url='http://111.11.196.111/aspx/corpinfo/CorpInfo.aspx?'
                                 'corpname=&cert=&PageIndex=%s' % int(page),
                             callback=self.parse,
                             meta={'page': page}
                             )

    def parse(self, response):
        a_href_all = Selector(response=response).xpath('//table[@class="table table-striped table-bordered"]'
                                                       '/tbody/tr/td[2]/a/@href')
        for t in a_href_all:
            a_url = t.extract()
            a_url = a_url.split('../..')[1]
            re_a = self.bigurl + a_url
            print(re_a)
            yield scrapy.Request(url=re_a, callback=self.company_information)
        page = int(response.meta['page'])
        page -= 1
        if page != 0:
            print(page)
            yield scrapy.Request(url='http://111.11.196.111/aspx/corpinfo/CorpInfo.aspx?'
                                     'corpname=&cert=&PageIndex=%s' % page,
                                 callback=self.parse,
                                 meta={'page': page}
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
        company_name = Selector(response=response).xpath('//td[@id="corpname"]/text()').extract_first()
        repeat = self.r.sadd('Company_name', company_name + '西藏自治区')
        if repeat:
            licenseNum = Selector(response=response).xpath('//td[@id="corpcode"]/text()').extract_first()
            contactMan = Selector(response=response).xpath('//td[@id="linkman"]/text()').extract_first()
            address = Selector(response=response).xpath('//td[@id="address"]/text()').extract_first()
            province = Selector(response=response).xpath('//td[@id="province"]/text()').extract_first()
            if province != '西藏自治区':
                data['companyArea'] = ''
                data['area'] = '西藏自治区'
                person_register = Selector(response=response). \
                    xpath('//div[@id="company_info_register_engineers"]/table/tbody/tr/td/a/@href')
                for p in person_register:
                    p = p.extract().split('../aspx/userinfo')[1]
                    re_a = 'http://111.11.196.111/aspx/userinfo' + p
                    yield scrapy.Request(url=re_a,
                                         callback=self.person_info,
                                         dont_filter=True,
                                         meta={'person': 1, 'licenseNum': licenseNum}
                                         )

                person_title = Selector(response=response). \
                    xpath('//div[@id="company_info_no_register_engineers"]/table/tbody/tr/td/a/@href')
                for p in person_title:
                    print('fffffffffffffffffffffffffffffffffffff')
                    p = p.extract().split('../aspx/userinfo')[1]
                    re_a = 'http://111.11.196.111/aspx/userinfo' + p
                    yield scrapy.Request(url=re_a,
                                         callback=self.person_info,
                                         dont_filter=True,
                                         meta={'person': 0, 'licenseNum': licenseNum}
                                         )
            else:
                data['area'] = ''
                data['companyArea'] = '西藏自治区'

            data['companyName'] = company_name
            data['token'] = self.token
            data['contactMan'] = contactMan
            data['contactAddress'] = address
            data['contactPhone'] = ''
            if licenseNum is not None:
                if len(licenseNum) != 18:
                    data['licenseNum'] = ''
                else:
                    data['licenseNum'] = licenseNum
            else:
                data['licenseNum'] = ''
            # print(data)
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

    def person_info(self, response):
        print('zzzzzzzzzzzzzzzzzzzzzzzz')
        if response.meta['person'] == 1:
            person_data = {'companyName': '',
                           'licenseNum': response.meta['licenseNum'], 'name': '', 'area': '西藏自治区', 'sex': '',
                           'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                           'validTime': '', 'tel': '', 'tokenKey': self.token
                           }
            name = Selector(response=response).xpath('//td[@id="PersonName"]/text()').extract_first()
            if name:
                person_data['name'] = name

            sex = Selector(response=response).xpath('//td[@id="Sex"]/text()').extract_first()
            if sex:
                person_data['sex'] = sex

            id_card = Selector(response=response).xpath('//td[@id="idcard"]/text()').extract_first()
            if id_card:
                person_data['idCard'] = id_card

            every_card_person = Selector(response=response).xpath('//div[@id="engineer_info_zhiye"]/table')
            for e in every_card_person:
                grade = e.xpath('./thead/tr/th/text()').extract_first()
                if grade:
                    person_data['grade'] = grade

                company_name = e.xpath('./tbody/tr[1]/td/a/text()').extract_first()
                if company_name:
                    person_data['companyName'] = company_name
                else:
                    company_name = ''

                validTime = e.xpath('./tbody/tr[2]/td[4]/text()').extract_first()
                if validTime:
                    person_data['validTime'] = validTime

                major = e.xpath('./tbody/tr[3]/td[2]/text()').extract_first()
                if major:
                    person_data['major'] = major
                print(person_data, '注册人员')
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': company_name},
                    dont_filter=True,
                )

        else:
            person_data = {'companyName': '',
                           'licenseNum': response.meta['licenseNum'], 'name': '', 'area': '西藏自治区', 'sex': '',
                           'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                           'validTime': '', 'tel': '', 'tokenKey': self.token
                           }
            name = Selector(response=response).xpath('//td[@id="PersonName"]/text()').extract_first()
            if name:
                person_data['name'] = name

            sex = Selector(response=response).xpath('//td[@id="Sex"]/text()').extract_first()
            if sex:
                person_data['sex'] = sex

            id_card = Selector(response=response).xpath('//td[@id="idcard"]/text()').extract_first()
            if id_card:
                person_data['idCard'] = id_card

            every_card_person = Selector(response=response).xpath('//div[@id="engineer_info_gangwei"]/table')
            for e in every_card_person:
                major = e.xpath('./thead/tr/th/text()').extract_first()
                if major:
                    person_data['major'] = major

                company_name = e.xpath('./tbody/tr[1]/td/a/text()').extract_first()
                if company_name:
                    person_data['companyName'] = company_name
                else:
                    company_name = ''

                validTime = e.xpath('./tbody/tr[2]/td[4]/text()').extract_first()
                if validTime:
                    person_data['validTime'] = validTime

                print(person_data, '非注册人员')
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': company_name},
                    dont_filter=True,
                )

    def person_post(self, response):
        not_company_code = json.loads(response.text)['code']
        print(response.text, response.meta['company_name'])
        if not_company_code == -118 or not_company_code == -102:
            self.r.sadd('title_name1', response.meta['company_name'])
            self.r.sadd('title_name3', response.meta['company_name'])
            print('当前公司不存在已经正在添加')
        else:
            print(response.meta['data']['name'], '添加成功')
