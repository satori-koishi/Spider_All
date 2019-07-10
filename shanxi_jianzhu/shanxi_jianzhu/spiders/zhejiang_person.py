# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json


class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'zhejiang_person'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://115.29.2.37:8080/enterprise_sw.php?p=1'
        self.index = 1
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {'area': '浙江省', 'companyArea': '', 'contactPhone': '', 'token': self.token, 'contactAddress': '',
                     'contactMan': '', 'licenseNum': ''}
        self.bigurl = 'http://115.29.2.37:8080/'

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        tr = Selector(response=response).xpath('//table[@class="t1"]/tr[@class="auto_h"]')
        for t in tr:
            company_name = t.xpath('./td/div/a/@title').extract_first()
            company_url = t.xpath('./td/div/a/@href').extract_first()
            number = t.xpath('./td[3]/text()').extract_first()
            number = number.split()
            if number:
                number = number[0]
                if len(number) == 18:
                    number = number
                    self.data['number'] = ''
            else:
                number = ''
            self.data['companyName'] = company_name
            yield scrapy.Request(url=self.bigurl + company_url,
                                 callback=self.company_information,
                                 meta={'company_name': company_name, 'number': number}
                                 )

        self.index = self.index + 1
        if self.index != 285:
            yield scrapy.Request(url='http://115.29.2.37:8080/enterprise_sw.php?p=%s' % self.index, callback=self.parse,
                                 dont_filter=True)

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
        person_info = Selector(response=response).xpath('//div[@class="classContent t2"]/table/tr')
        del person_info[0]
        print(response.meta['company_name'], 'kkkkkkkkkkkkkkkkkkk')
        # 注册人员
        if person_info != 0:
            for p in person_info:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': response.meta['number'], 'name': '', 'area': '浙江省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                               'validTime': '', 'tel': '', 'tokenKey': self.token
                               }
                info = p.xpath('./td')

                # 姓名
                name = info[1].xpath('./a/text()').extract_first().split()
                if name is not None:
                    person_data['name'] = name[0]

                # 身份证
                card = info[2].xpath('text()').extract_first()
                if card is not None:
                    person_data['idCard'] = card

                # 注册类型及等级
                grade = info[3].xpath('text()').extract_first()
                if grade is not None:
                    person_data['grade'] = grade

                # 注册专业
                major = info[4].xpath('text()').extract_first()
                if major is not None:
                    person_data['major'] = major

                # 注册证书编号
                num = info[5].xpath('text()').extract_first()
                if num is not None:
                    person_data['num'] = num

                # 有效期至
                validTime = info[7].xpath('text()').extract_first()
                if validTime is not None:
                    validTime = validTime.replace('/', '-')
                    person_data['validTime'] = validTime
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': response.meta['company_name']},
                    dont_filter=True,
                )
                print(person_data, '注册人员AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                # print(name)

        # 职称人员
        person_title = Selector(response=response).xpath('//div[@class="classContent t3"]/table/tr')
        del person_title[0]
        if person_title != 0:
            for p in person_title:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': response.meta['number'], 'name': '', 'area': '浙江省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                               'validTime': '', 'tel': '', 'tokenKey': self.token
                               }
                info = p.xpath('./td')

                # 姓名
                name = info[1].xpath('./a/text()').extract_first().split()
                if name is not None:
                    person_data['name'] = name[0]

                # 身份证
                card = info[2].xpath('text()').extract_first()
                if card is not None:
                    person_data['idCard'] = card

                # 注册类型及等级
                grade = info[3].xpath('text()').extract_first()
                if grade is not None:
                    person_data['grade'] = grade

                # 注册专业
                major = info[4].xpath('text()').extract_first()
                if major is not None:
                    person_data['major'] = major

                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': response.meta['company_name']},
                    dont_filter=True,
                )
                print(person_data, '职称人员bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')

        # 现场人员
        person_scene = Selector(response=response).xpath('//div[@class="classContent t4"]/table/tr')
        del person_scene[0]
        if person_scene != 0:
            for p in person_scene:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': response.meta['number'], 'name': '', 'area': '浙江省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                               'validTime': '', 'tel': '', 'tokenKey': self.token
                               }
                info = p.xpath('./td')

                # 姓名
                name = info[1].xpath('./a/text()').extract_first().split()
                if name is not None:
                    person_data['name'] = name[0]

                # 证件号码
                card = info[2].xpath('text()').extract_first()
                if card is not None:
                    person_data['idCard'] = card

                # 人员类型
                major = info[3].xpath('text()').extract_first()
                if major is not None:
                    person_data['major'] = major

                # 证书编号
                number = info[4].xpath('text()').extract_first()
                if number is not None:
                    person_data['num'] = number

                # 有效期至
                validTime = info[6].xpath('text()').extract_first()
                if validTime is not None:
                    validTime = validTime.replace('/', '-')
                    person_data['validTime'] = validTime
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': response.meta['company_name']},
                    dont_filter=True,
                )
                print(person_data, '现场人员ccccccccccccccccccccccccccccccccc')

        # 技术人员
        person_scene = Selector(response=response).xpath('//div[@class="classContent t5"]/table/tr')
        del person_scene[0]
        if person_scene != 0:
            for p in person_scene:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': response.meta['number'], 'name': '', 'area': '浙江省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                               'validTime': '', 'tel': '', 'tokenKey': self.token
                               }
                info = p.xpath('./td')

                # 姓名
                name = info[1].xpath('./a/text()').extract_first().split()
                if name is not None:
                    person_data['name'] = name[0]

                # 身份证
                card = info[2].xpath('text()').extract_first()
                if card is not None:
                    person_data['idCard'] = card

                # 人员类型
                major = info[3].xpath('text()').extract_first()
                if major is not None:
                    person_data['major'] = major

                # 注册证书编号
                number = info[4].xpath('text()').extract_first()
                if number is not None:
                    person_data['num'] = number

                # 有效期
                validTime = info[6].xpath('text()').extract_first()
                if validTime is not None:
                    validTime = validTime.replace('/', '-')
                    person_data['validTime'] = validTime
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': response.meta['company_name']},
                    dont_filter=True,
                )
                print(person_data, '技术人员DDDDDDDDDDDDDDDDDDDDDDDDDDD')

    def person_post(self, response):
        not_company_code = json.loads(response.text)['code']
        print(response.text, response.meta['company_name'])
        if not_company_code == -118 or not_company_code == -102:
            self.r.sadd('title_name1', response.meta['company_name'])
            self.r.sadd('title_name3', response.meta['company_name'])
            print('当前公司不存在已经正在添加')
        else:
            print(response.meta['data']['name'], '添加成功')
