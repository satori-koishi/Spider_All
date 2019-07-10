# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re


class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'another_province_into_fujian'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/CompanyQuery.aspx?bussinessSystemID=31'
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.index = 1
        self.x = True
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {'companyName': '', 'contactMan': '',
                     'companyArea': '', 'area': '福建省', 'contactAddress': '',
                     'contactPhone': '',
                     'licenseNum': '',
                     'token': self.token}
        self.bigurl = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/'

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        post_forama_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        post_forama_data['__VIEWSTATE'] = __VIEWSTATE
        post_forama_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        post_forama_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        post_forama_data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder$pGrid$nextpagebtn'
        post_forama_data['ctl00$ContentPlaceHolder$ddlBussinessSystem'] = '31'

        tr = Selector(response=response).xpath('//table[@id="ctl00_ContentPlaceHolder_gvDemandCompany"]/tr/td/a/@href')
        for t in tr:
            tip = t.extract()
            yield scrapy.Request(url=self.bigurl + tip, callback=self.company_information,
                                 meta={'url_zz': tip},
                                 dont_filter=True)

        self.index = self.index + 1
        if not self.index == 4339:
            yield scrapy.FormRequest(url=self.url,
                                     formdata=post_forama_data,
                                     callback=self.parse
                                     )

    def company_information(self, response):
        td = Selector(response=response).xpath('//table[@class="form orange"]/tr')
        company_name = td[0].xpath('./td/text()').extract_first()
        company_name = company_name.split()[0]
        licenseNum = td[3].xpath('./td[3]/text()').extract_first()
        licenseNum = licenseNum.split()
        if licenseNum:
            licenseNum = licenseNum[0]
            if len(licenseNum) == 18:
                self.data['licenseNum'] = licenseNum
        else:
            licenseNum = ''
        self.data['companyName'] = company_name
        # print(self.data)
        # yield scrapy.Request(
        #     url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
        #     # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
        #     method="POST",
        #     headers={'Content-Type': 'application/json'},
        #     body=json.dumps(self.data),
        #     callback=self.zz,
        #     meta={'company_name': company_name, 'data': self.data},
        #     dont_filter=True
        # )
        # print('http://220.160.52.164:96/ConstructionInfoPublish/Pages/RegisterPersonInfo.aspx?' +
        #       response.meta['url_zz'], 'zzzzzzzzzzzzzzzzzzzz')

        tip = response.meta['url_zz'].replace('CompanyInfo.aspx?', '')

        url_register = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/RegisterPersonInfo.aspx?' \
                       + tip + '&index=0&'

        # 注册人员
        yield scrapy.Request(
            url=url_register,
            # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
            callback=self.person_zz,
            meta={'company_name': company_name, 'number': licenseNum},
            dont_filter=True
        )

        ManagerInfo = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/ManagerInfo.aspx?' \
                      + tip + '&index=0&'
        # # 管理人员
        yield scrapy.Request(
            url=ManagerInfo,
            meta={'company_name': company_name, 'number': licenseNum},
            dont_filter=True,
            callback=self.person_zz
        )

        TitleManInfo = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/TitleManInfo.aspx?' \
                       + tip + '&index=0&'
        # 职称人员
        yield scrapy.Request(
            url=TitleManInfo,
            callback=self.person_zz,
            meta={'company_name': company_name, 'number': licenseNum},
            dont_filter=True
        )

        LiablePersonInfo = 'http://220.160.52.164:96/ConstructionInfoPublish/Pages/LiablePersonInfo.aspx?' \
                      + tip + '&index=0&'
        # 安全人员
        yield scrapy.Request(
            url=LiablePersonInfo,
            callback=self.person_zz,
            meta={'company_name': company_name, 'number': licenseNum},
            dont_filter=True
        )

    def person_zz(self, response):
        register = Selector(response=response).xpath('//div[@id="divPerson"]/table[@class="t grey"]/tr')

        # 注册人员
        if register:
            del register[0]
            for p in register:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': response.meta['number'],
                               'name': '', 'area': '福建省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '',
                               'num': '', 'regNum': '', 'validTime': '',
                               'tel': '', 'tokenKey': self.token}
                info = p.xpath('./td')

                # 姓名
                name = info[0].xpath('text()').extract_first().split()
                if name:
                    person_data['name'] = name[0]
                else:
                    person_data['name'] = ''

                # 注册执业证书类别及等级
                grade = info[1].xpath('text()').extract_first()
                if grade:
                    person_data['grade'] = grade
                else:
                    person_data['grade'] = ''

                # 注册专业
                major = info[2].xpath('text()').extract_first()
                if major:
                    person_data['major'] = major
                else:
                    person_data['major'] = ''

                # 注册编号
                regNum = info[3].xpath('text()').extract_first()
                if regNum:
                    person_data['regNum'] = regNum
                else:
                    person_data['regNum'] = ''

                # 注册编号
                num = info[4].xpath('text()').extract_first()
                if num:
                    person_data['num'] = num
                else:
                    person_data['num'] = ''

                # 证书有效期
                validTime = info[6].xpath('text()').extract_first()
                if validTime:
                    person_data['validTime'] = validTime
                else:
                    person_data['validTime'] = ''
                print(person_data, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': response.meta['company_name']},
                    dont_filter=True,
                )
        else:
            print('--%s--没有注册人员' % response.meta['company_name'])

        # 现场管理人员
        managerInfo = Selector(response=response).xpath('//div[@id="divManager"]/table[@class="t grey"]/tr')
        if managerInfo:
            del managerInfo[0]
            for p in managerInfo:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': response.meta['number'],
                               'name': '', 'area': '福建省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '',
                               'num': '', 'regNum': '', 'validTime': '',
                               'tel': '', 'tokenKey': self.token}
                info = p.xpath('./td')

                # 姓名
                name = info[0].xpath('text()').extract_first()
                if name:
                    person_data['name'] = name
                else:
                    person_data['name'] = ''

                # 岗位类别
                grade = info[1].xpath('text()').extract_first().split()
                if grade:
                    person_data['grade'] = grade[0]
                else:
                    person_data['grade'] = ''

                # 注册编号
                num = info[2].xpath('text()').extract_first()
                if num:
                    person_data['num'] = num
                else:
                    person_data['num'] = ''

                # 证书有效期
                validTime = info[4].xpath('text()').extract_first()
                if validTime:
                    person_data['validTime'] = validTime
                else:
                    person_data['validTime'] = ''
                print(person_data, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': response.meta['company_name']},
                    dont_filter=True,
                )
        else:
            print('--%s--没有现场人员' % response.meta['company_name'])

        # 中级以上职称人员
        TitleManInfo = Selector(response=response).xpath('//div[@id="divTitleMain"]/table[@class="t grey"]/tr')
        if TitleManInfo:
            del TitleManInfo[0]
            for p in TitleManInfo:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': response.meta['number'],
                               'name': '', 'area': '福建省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '',
                               'num': '', 'regNum': '', 'validTime': '',
                               'tel': '', 'tokenKey': self.token}
                info = p.xpath('./td')

                # 姓名
                name = info[0].xpath('./span/text()').extract_first()
                if name:
                    person_data['name'] = name
                else:
                    person_data['name'] = ''

                # 职称类别
                grade = info[2].xpath('text()').extract_first().split()
                if grade:
                    person_data['grade'] = grade[0]
                else:
                    person_data['grade'] = ''

                # 职称编号
                num = info[1].xpath('text()').extract_first()
                if num:
                    person_data['num'] = num
                else:
                    person_data['num'] = ''

                # 职称专业
                major = info[3].xpath('text()').extract_first()
                if major:
                    print(major)
                    if major is not '无' or major is not '/':
                        person_data['major'] = major
                else:
                    person_data['major'] = ''
                print(person_data, 'cccccccccccccccccccccccccccccccccccccccc')
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': response.meta['company_name']},
                    dont_filter=True,
                )

        else:
            print('--%s--中级以上职称人员' % response.meta['company_name'])

        # 安全证三类人员
        LiablePersonInfo = Selector(response=response).xpath('//div[@id="divLiable"]/table[@class="t grey"]/tr')
        if LiablePersonInfo:
            del LiablePersonInfo[0]
            for p in LiablePersonInfo:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': response.meta['number'],
                               'name': '', 'area': '福建省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '',
                               'num': '', 'regNum': '', 'validTime': '',
                               'tel': '', 'tokenKey': self.token}
                info = p.xpath('./td')

                # 姓名
                name = info[0].xpath('text()').extract_first()
                if name:
                    person_data['name'] = name
                else:
                    person_data['name'] = ''

                # 证书类型
                grade = info[1].xpath('text()').extract_first().split()
                if grade:
                    person_data['grade'] = grade[0]
                else:
                    person_data['grade'] = ''

                # 证书编号
                num = info[2].xpath('text()').extract_first()
                if num:
                    person_data['num'] = num
                else:
                    person_data['num'] = ''

                # 证书有效期
                validTime = info[3].xpath('text()').extract_first()
                if validTime:
                    person_data['validTime'] = validTime
                else:
                    person_data['validTime'] = ''
                print(person_data, 'dddddddddddddddddddddddddddddddddddddd')
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_data,
                    callback=self.person_post,
                    meta={'data': person_data, 'company_name': response.meta['company_name']},
                    dont_filter=True,
                )
        else:
            print('--%s--安全证三类人员' % response.meta['company_name'])

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