# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re


class GuangXiProvince(scrapy.Spider):
    name = 'GuangXiProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://dn4.gxzjt.gov.cn:1141/WebInfo/Enterprise/Enterprise.aspx'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://dn4.gxzjt.gov.cn:1141/WebInfo/Enterprise/'
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse,
                             )

    def parse(self, response):
        post_forama_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        post_forama_data['__VIEWSTATE'] = __VIEWSTATE
        post_forama_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        post_forama_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        post_forama_data['__EVENTARGUMENT'] = '1'
        post_forama_data['ctl00$ctl00$ContentPlaceHolder1$Search$DanWeiType'] = ''
        post_forama_data['ctl00$ctl00$ContentPlaceHolder1$Search$BtnSearch'] = '搜索'
        search_id = [13, 18, 10, 14, 30, 20, 22, 16, 24, 11, 15]
        for i in search_id:
            post_forama_data['ctl00$ctl00$ContentPlaceHolder1$Search$DanWeiType'] = str(i)
            yield scrapy.FormRequest(url=self.url, formdata=post_forama_data, callback=self.type_city,
                                     meta={'WeiType': i, 'now_page': 1}
                                     )

    def person_post(self, response):
        not_company_code = json.loads(response.text)['code']
        print(response.text)
        if not_company_code == -118:
            self.r.sadd('title_name1', response.meta['company_name'])
            self.r.sadd('title_name3', response.meta['company_name'])
            print('当前公司不存在已经正在添加')
        else:
            print(response.meta['data']['name'], '添加成功')

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
        print(response.url, 'zzzzzzzzzzzzzzz')
        data = {'licenseNum': '', 'contactMan': '', 'contactAddress': '', 'companyArea': '', 'area': '',
                'contactPhone': '', 'token': self.token}
        company_name = Selector(response=response).xpath(
            '//span[@id="ContentPlaceHolder1_DanWeiName_8344"]/text()').extract_first()
        repeat = self.r.sadd('Company_name', company_name + '广西省')
        repeat = 1
        if repeat:
            data['companyName'] = company_name

            number = Selector(response=response).xpath(
                '//span[@id="ContentPlaceHolder1_UnitOrgNum_8344"]/text()').extract_first()
            if number is not None:
                if len(number) == 18:
                    data['licenseNum'] = number

            contact_man = Selector(response=response).xpath(
                '//span[@id="ContentPlaceHolder1_LocalLianXiRen_8346"]/text()').extract_first()
            if contact_man is not None:
                data['contactMan'] = contact_man

            contact_address = Selector(response=response).xpath(
                '//span[@id="ContentPlaceHolder1_Address_8346"]/text()').extract_first()
            if contact_address is not None:
                data['contactAddress'] = contact_address

            just_province = Selector(response=response).xpath(
                '//span[@id="ContentPlaceHolder1_AreaName_8344"]/text()').extract_first()
            if just_province is not None:
                just_province = just_province.split('·')[0]
                if just_province == '广西壮族自治区':
                    data['companyArea'] = '广西壮族自治区'
                    data['area'] = ''
                else:
                    data['companyArea'] = ''
                    data['area'] = '广西壮族自治区'
                    person_info = Selector(response=response).xpath('//table[@id="ContentPlaceHolder1_DataGrid1"]/tr')
                    print(len(person_info), 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
                    if len(person_info) != 1:
                        del person_info[0]
                        for p in person_info:
                            person_data = {'companyName': company_name, 'licenseNum': number, 'area': '广西壮族自治区',
                                           'sex': '',
                                           'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                                           'validTime': '',
                                           'tel': '', 'tokenKey': self.token}
                            info = p.xpath('./td')

                            name = info[1].xpath('./a/text()')
                            if name is not None:
                                person_data['name'] = name.extract_first().split()[0]
                            else:
                                continue

                            id_card = info[2].xpath('text()')
                            if id_card.extract_first().split():
                                person_data['idCard'] = id_card.extract_first().split()[0]

                            grade = info[3].xpath('text()')
                            if grade.extract_first().split():
                                grade = grade.extract_first().split()[0]
                                if grade != '暂无':
                                    person_data['grade'] = grade

                            major = info[4].xpath('text()')
                            if major.extract_first().split():
                                person_data['major'] = major.extract_first().split()[0]

                            reg_num = info[5].xpath('text()')
                            if reg_num.extract_first().split():
                                person_data['regNum'] = reg_num.extract_first().split()[0]

                            valid_time = info[6].xpath('text()')
                            if valid_time.extract_first().split():
                                valid_time = valid_time.extract_first().split()[0]
                                person_data['validTime'] = valid_time.replace('/', '-')

                            print(person_data, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
                            yield scrapy.FormRequest(url='https://api.maotouin.com/rest/'
                                                         'companyInfo/addCompanyRecordEngineer.htm',
                                                     formdata=person_data,
                                                     callback=self.person_zz,
                                                     meta={'company_name': company_name},
                                                     dont_filter=True
                                                     )
                    else:
                        print(len(person_info), '对不起当前公司无人人存在')
            else:
                self.r.sadd('title_name1', company_name)
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
            print(data)
        else:
            print('此公司信息已经存在', company_name)

    def type_city(self, response):
        post_forama_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        post_forama_data['__VIEWSTATE'] = __VIEWSTATE
        post_forama_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        post_forama_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        post_forama_data['__EVENTTARGET'] = 'ctl00$ctl00$ContentPlaceHolder1$List$Pager'
        post_forama_data['__EVENTARGUMENT'] = '1'
        post_forama_data['ctl00$ctl00$ContentPlaceHolder1$Search$DanWeiType'] = str(response.meta['WeiType'])
        page = Selector(response=response).xpath('//td[@align="left"]/text()').extract_first()
        xx = '当前第\d+/(\d+)页 共\d+条记录 每页10条'
        page = re.findall(xx, page)[0]
        print('AAAAAAAAAAAAAAAAAAAAAAAAAA -------%s' % page)
        company_all = Selector(response=response).xpath('//a[@target="_blank"]/@href')
        for c in company_all:
            yield scrapy.Request(url=self.bigurl + c.extract(), callback=self.company_information,
                                 meta={'type_cc': response.meta['WeiType']},
                                 dont_filter=True
                                 )
        index = response.meta['now_page']
        index += 1
        if index != page:
            post_forama_data['__EVENTARGUMENT'] = str(index)
            yield scrapy.FormRequest(url=self.url, formdata=post_forama_data,
                                     meta={'now_page': index, 'WeiType': response.meta['WeiType']},
                                     callback=self.type_city,
                                     dont_filter=True
                                     )

    def person_zz(self, response):
        not_company_code = json.loads(response.text)['code']
        not_search_company_name = response.meta['company_name']
        self.r.sadd('all_company_name', not_search_company_name)
        print(response.text)
        if not_company_code == -118 or not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_name3', not_search_company_name)
        else:
            print('当前人员添加完成')
