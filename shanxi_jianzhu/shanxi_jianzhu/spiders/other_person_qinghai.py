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
    name = 'other_province_qinghai'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://jzsc.qhcin.gov.cn/dataservice/query/staff/list'
        self.index = 1
        self.flag = True
        self.into = 'XX'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://jzsc.qhcin.gov.cn'

    def start_requests(self):
        for i in range(1, 7):
            yield scrapy.FormRequest(url=self.url, formdata={'region_zone': self.into,
                                                             'staff_type': str(i)
                                                             },
                                     callback=self.parse,
                                     meta={'page': 1, 'staff_type': i}
                                     )

    def parse(self, response):

        a_href_all = Selector(response=response).xpath('//table[@class="table_box"]/tbody/tr/@onclick')
        print(len(a_href_all))
        for t in a_href_all:
            a_url = t.extract()
            re_a = 'javascript:location.href=\'(.*)\''
            re_a = re.findall(re_a, a_url)[0]
            re_a = self.bigurl + re_a
            yield scrapy.Request(url=re_a, callback=self.person_info,
                                 meta={'staff_type': response.meta['staff_type']
                                       },
                                 dont_filter=True
                                 )
        page = Selector(response=response).xpath("//a[@sf='pagebar']").extract_first()
        page_info = re.findall('tt:(\d+),pn:\d+,pc:(\d+),', page)
        page = page_info[0][1]
        send_data = {'staff_type': str(response.meta['staff_type']),
                     '$total': str(page_info[0][0]),
                     'region_zone': 'XX',
                     '$reload': '0',
                     '$pgsz': '15'
                     }
        index = int(response.meta['page'])
        index = index + 1
        if index != page:
            send_data['$pg'] = str(index)
            yield scrapy.FormRequest(url=self.url,
                                     formdata=send_data,
                                     callback=self.parse,
                                     meta={'staff_type': response.meta['staff_type'],
                                           'page': index}
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

    def person_info(self, response):
        mane_id = Selector(response=response).xpath('//span[@class="user-name"]/text()').extract_first()
        xx = '(.*) 【(.*)】'
        company_name = Selector(response=response).xpath('//b[@style="cursor:pointer; "]/text()').extract_first()
        # print(company_name, 'zzzzzzzzzzzzzzzzz')

        person = re.findall(xx, mane_id)
        select_person_type = ['staff/logCertList/', 'staff/titleCertList/', 'staff/safetyCertList/',
                              'staff/keysCertList/', 'staff/techCertList/', 'staff/specialCertList/'
                              ]
        small_url = select_person_type[response.meta['staff_type'] - 1]
        registered = re.sub('staff/.*/', small_url, response.url)
        yield scrapy.Request(url=registered, callback=self.person_registered,
                             meta={'staff_type': response.meta['staff_type'],
                                   'person_name': person[0][0],
                                   'id_card': person[0][1],
                                   'company_name': company_name
                                   },
                             dont_filter=True
                             )
        # print('姓名：%s---身份号：%s---' % (person[0][0], person[0][1]))

    def person_registered(self, response):
        # print()
        test = Selector(response=response).xpath('//dl/div/text()').extract_first()
        if test is not '没有数据':
            if response.meta['staff_type'] == 1:
                info_data = Selector(response=response).xpath('//dl')
                for i in info_data:
                    person_data = {'companyName': response.meta['company_name'],
                                   'licenseNum': '', 'name': response.meta['person_name'], 'area': '青海省', 'sex': '',
                                   'idCard': response.meta['id_card'], 'grade': '', 'major': '', 'num': '', 'regNum': '',
                                   'validTime': '', 'tel': '', 'tokenKey': self.token
                                   }
                    dd = i.xpath('./dd')

                    # 注册类别
                    grade = dd[0].xpath('./b/text()').extract_first()
                    if grade:
                        person_data['grade'] = grade

                    # 注册专业
                    major = dd[1].xpath('./text()').extract_first()
                    if major:
                        person_data['major'] = major

                    # 注册号
                    num = dd[3].xpath('./text()').extract_first()
                    if num:
                        person_data['num'] = num
                    print(person_data, '注册人员')
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': response.meta['company_name']},
                        dont_filter=True,
                    )
            elif response.meta['staff_type'] == 2:
                info_data = Selector(response=response).xpath('//dl')
                for i in info_data:
                    person_data = {'companyName': response.meta['company_name'],
                                   'licenseNum': '', 'name': response.meta['person_name'], 'area': '青海省', 'sex': '',
                                   'idCard': response.meta['id_card'], 'grade': '', 'major': '', 'num': '', 'regNum': '',
                                   'validTime': '', 'tel': '', 'tokenKey': self.token
                                   }
                    dd = i.xpath('./dd')

                    # 注册类别
                    try:
                        grade = dd[0].xpath('./b/text()').extract_first()
                    except IndexError:
                        continue
                    if grade:
                        person_data['grade'] = grade

                    # 注册专业
                    major = dd[1].xpath('./text()').extract_first()
                    if major:
                        person_data['major'] = major

                    # 职称编号
                    num = dd[2].xpath('./text()').extract_first()
                    if num:
                        person_data['num'] = num
                    print(person_data, '职业人员')
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': response.meta['company_name']},
                        dont_filter=True,
                    )
            elif response.meta['staff_type'] == 3:
                info_data = Selector(response=response).xpath('//dl')
                for i in info_data:
                    person_data = {'companyName': response.meta['company_name'],
                                   'licenseNum': '', 'name': response.meta['person_name'], 'area': '青海省', 'sex': '',
                                   'idCard': response.meta['id_card'], 'grade': '', 'major': '', 'num': '', 'regNum': '',
                                   'validTime': '', 'tel': '', 'tokenKey': self.token
                                   }
                    dd = i.xpath('./dd')

                    # 注册专业
                    number = dd[3].xpath('./text()').extract_first()
                    if number:
                        person_data['num'] = number

                    # # 职称编号
                    # validTime = dd[4].xpath('./text()').extract_first()
                    # if validTime:
                    #     person_data['validTime'] = validTime.replace('/')
                    print(person_data, '安全三类人员')
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': response.meta['company_name']},
                        dont_filter=True,
                    )

            elif response.meta['staff_type'] == 4:
                info_data = Selector(response=response).xpath('//dl')
                for i in info_data:
                    person_data = {'companyName': response.meta['company_name'],
                                   'licenseNum': '', 'name': response.meta['person_name'], 'area': '青海省', 'sex': '',
                                   'idCard': response.meta['id_card'], 'grade': '', 'major': '', 'num': '', 'regNum': '',
                                   'validTime': '', 'tel': '', 'tokenKey': self.token
                                   }
                    dd = i.xpath('./dd')

                    # 注册专业
                    try:
                        major = dd[0].xpath('./text()').extract_first()
                    except IndexError:
                        continue
                    if major:
                        person_data['major'] = major

                    # 资格专业
                    grade = dd[1].xpath('./text()').extract_first()
                    if grade:
                        person_data['grade'] = grade

                    # 证书编号
                    num = dd[3].xpath('./text()').extract_first()
                    if num:
                        person_data['num'] = num

                    # # 职称编号
                    # validTime = dd[4].xpath('./text()').extract_first()
                    # if validTime:
                    #     person_data['validTime'] = validTime
                    print(person_data, '专业岗位证书')
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': response.meta['company_name']},
                        dont_filter=True,
                    )

            elif response.meta['staff_type'] == 5:
                info_data = Selector(response=response).xpath('//dl')
                for i in info_data:
                    person_data = {'companyName': response.meta['company_name'],
                                   'licenseNum': '', 'name': response.meta['person_name'], 'area': '青海省', 'sex': '',
                                   'idCard': response.meta['id_card'], 'grade': '', 'major': '', 'num': '', 'regNum': '',
                                   'validTime': '', 'tel': '', 'tokenKey': self.token
                                   }
                    dd = i.xpath('./dd')

                    # 注册专业
                    major = dd[0].xpath('./text()').extract_first()
                    if major:
                        person_data['major'] = major

                    # 资格专业
                    grade = dd[1].xpath('./text()').extract_first()
                    if grade:
                        person_data['grade'] = grade

                    # 证书编号
                    num = dd[3].xpath('./text()').extract_first()
                    if num:
                        person_data['num'] = num

                    # 有效期至
                    validTime = dd[4].xpath('./text()').extract_first()
                    if validTime:
                        person_data['validTime'] = validTime
                    print(person_data, '技术人员')
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': response.meta['company_name']},
                        dont_filter=True,
                    )

            elif response.meta['staff_type'] == 6:
                info_data = Selector(response=response).xpath('//dl')
                for i in info_data:
                    person_data = {'companyName': response.meta['company_name'],
                                   'licenseNum': '', 'name': response.meta['person_name'], 'area': '青海省', 'sex': '',
                                   'idCard': response.meta['id_card'], 'grade': '', 'major': '', 'num': '', 'regNum': '',
                                   'validTime': '', 'tel': '', 'tokenKey': self.token
                                   }
                    dd = i.xpath('./dd')

                    # 资格类别
                    try:
                        major = dd[0].xpath('./text()').extract_first()
                    except IndexError:
                        continue
                    if major:
                        person_data['major'] = major

                    # 等级
                    grade = dd[1].xpath('./text()').extract_first()
                    if grade:
                        person_data['grade'] = grade

                    # 等级
                    num = dd[3].xpath('./text()').extract_first()
                    if num:
                        person_data['num'] = num

                    # 职称编号
                    validTime = dd[4].xpath('./text()').extract_first()
                    if validTime:
                        person_data['validTime'] = validTime
                    print(person_data, '职业技能人员')
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': response.meta['company_name']},
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
