# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import re
import json
import time


class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'other_province_jiangxi'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://59.52.254.106:8893/outQueryEnterpriseAll'
        self.flag = True
        self.data = {}
        self.data['contactMan'] = ''
        self.data['companyArea'] = ''
        self.data['area'] = '江西省'
        self.data['contactPhone'] = ''
        self.bigurl = 'http://59.52.254.106:8093'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data['token'] = self.token
        self.index = 1
        self.page = None
        self.bigurl = 'http://59.52.254.106:8893/'
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        if self.flag:
            all_page = Selector(response=response).xpath('//span[@class="localPage"]')[1].xpath(
                'text()').extract_first()
            show_data = Selector(response=response).xpath('//span[@class="localPage"]')[2].xpath(
                'text()').extract_first()
            # all_page = Selector(response=response).xpath('//span[@class="localPage"]')
            page = int(int(all_page) / int(show_data)) + 2
            self.page = page
            self.flag = False
        print('当前总页数%s' % self.page)
        company_info_url = Selector(response).xpath('//table [@class="so_table table_width"]/tr/td[2]/a/@onclick')
        for one_c in company_info_url:
            url = one_c.extract()
            new_url = re.findall('winopen\(\'(.*)\',1100,600,\'详情\'\);', url)[0]
            new_url = self.bigurl + new_url
            print(new_url)
            yield scrapy.Request(url=new_url, callback=self.company_information, dont_filter=True)
        self.index = self.index + 1
        print('当前页码%s' % self.index)
        if self.index != self.page:
            url = 'http://59.52.254.106:8893/outQueryEnterpriseAll?pageIndex=%s' % self.index
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def company_information(self, response):

        company_name = Selector(response=response).xpath('//table[@class="table_width"]')[1].xpath(
            './tr[1]/td[1]/text()').extract_first()
        number = Selector(response=response).xpath('//table[@class="table_width"]')[1].xpath(
            './tr[1]/td[2]/text()').extract_first()
        address = Selector(response=response).xpath('//td[@colspan="3"]')[1].xpath('text()').extract_first()
        contact_person = Selector(response=response).xpath('//td[@colspan="3"]')[2].xpath('text()').extract_first()
        self.data['companyName'] = company_name.split()[0]
        if len(number) != 18 or number ==None:
            self.data['licenseNum'] = ''
        else:
            self.data['licenseNum'] = number

        if address.split() != None:
            address = address.split()[0]
            self.data['contactAddress'] = address
        else:
            self.data['contactAddress'] = ''

        if contact_person.split()!= None:
            contact_person = contact_person.split()[0]
            if len(contact_person) < 4:
                self.data['contactMan'] = contact_person
            else:
                contact_person = Selector(response=response).xpath('//td[@colspan="3"]')[3].xpath(
                    'text()').extract_first()
                self.data['contactMan'] = contact_person
        else:
            self.data['contactMan'] = ''
        print(self.data)
        yield scrapy.Request(
            url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
            # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
            method="POST",
            headers={'Content-Type': 'application/json'},
            body=json.dumps(self.data),
            callback=self.zz,
            meta={'company_name': company_name, 'data': self.data},dont_filter=True

        )
        import time
        # timestamp = int(time.time() * 1000)
        userid = Selector(response=response).xpath('//input[@id="userId"]/@value').extract_first()
        enQualificationType = Selector(response=response).xpath(
            '//input[@id="enQualificationType"]/@value').extract_first()
        registerPersonFalg = 'http://59.52.254.106:8893/toQueryEmployeeListJsonOut?userId=%s&enQualificationType=%s' \
                             '&registerPersonFalg=1' % (
                                 userid, enQualificationType)
        nonRegisterType = 'http://59.52.254.106:8893/toQueryEmployeeListJsonOut?userId=%s&enQualificationType=%s' \
                          '&technicalType=1' % (
                              userid, enQualificationType)
        data = {'page': '1', 'rows': '1000'}
        yield scrapy.FormRequest(
            url=registerPersonFalg,
            # url=nonRegisterType,
            formdata=data,
            headers={'Content-Type': ' application/x-www-form-urlencoded; charset=UTF-8'},
            callback=self.person_info,
            meta={'company_name': company_name,
                  'number': number},
            dont_filter=True

        )
        yield scrapy.FormRequest(
            url=nonRegisterType,
            formdata=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            callback=self.not_person_info,
            meta={'company_name': company_name,
                  'number': number},
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

    def person_info(self, response):
        now_person = json.loads(response.text)
        person_info = {'companyName': response.meta['company_name'], 'licenseNum': response.meta['number'],
                       'area': '江西省', 'sex': '', 'idCard': '', 'major': '', 'phone': '', 'tokenKey': self.token}
        for n in now_person['rows']:
            person_info = {'companyName': response.meta['company_name'], 'licenseNum': response.meta['number'],
                           'area': '江西省', 'sex': '', 'idCard': '', 'major': '', 'phone': '', 'tokenKey': self.token,
                           'name': n['name']}
            # 人员名称
            # print(n['name'])
            print('我是%s----公司是%s' % (n['name'], response.meta['company_name']))

            # 证书编号
            # print(n['registrationInfo'][0]['regCertificateNumber'])
            try:
                person_info['num'] = n['registrationInfo'][0]['regCertificateNumber']
            except KeyError as e:
                person_info['num'] = ''

            # 注册类别
            # print(n['registrationInfo'][0]['registerType']['name'])
            person_info['grade'] = n['registrationInfo'][0]['registerType']['name']
            # 注册专业
            try:
                person_info['major'] = n['registrationInfo'][0]['qualificationRegMajors'][0]['name']
            except KeyError as e:
                person_info['major'] = ''

            # 执业印章号
            print(n['registrationInfo'][0]['qualificationCertNumber'])
            person_info['regNum'] = n['registrationInfo'][0]['qualificationCertNumber']

            # 发证机关 ---待续
            # print(n['registrationInfo'][0]['issuedBy'])

            # 证件有效时间
            try:
                print(n['registrationInfo'][0]['registrationDt'])
                c = time.localtime(int(n['registrationInfo'][0]['registrationDt'] / 1000))
                use_time = time.strftime("%Y-%m-%d", c)
                use_time = str(use_time)
                person_info['validTime'] = use_time
            except KeyError as e:
                person_info['validTime'] = ''

            # print(person_info)
            print('注册人员信息%s' % person_info)
            yield scrapy.FormRequest(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                formdata=person_info,
                callback=self.person_zz,
                meta={'company_name': response.meta['company_name']},
                dont_filter=True
            )

    def not_person_info(self, response):
        now_person = json.loads(response.text)
        person_info = {'companyName': response.meta['company_name'], 'licenseNum': response.meta['number'],
                       'area': '江西省', 'sex': ''}

        for i in now_person['rows']:
            # 人员名称
            person_info['name'] = i['name']
            # 联系电话
            person_info['tel'] = i['mobileNum']
            # 身份证
            person_info['idCard'] = i['idNumber']
            # 职称专业
            if len(i['jobTitleCertInfo']) != 0:
                # 职称
                try:
                    person_info['grade'] = i['titleLevel']['name']
                except KeyError as e:
                    person_info['grade'] = ''
                # 职称专业
                person_info['major'] = i['jobTitleCertInfo'][0]['specificTitleMajor']
                # 证书编号
                person_info['num'] = i['jobTitleCertInfo'][0]['certificateNumber']
                # 发证时间
                try:
                    # 有效期
                    c = time.localtime(int(i['jobTitleCertInfo'][0]['issuedDt'] / 1000))
                    use_time = time.strftime("%Y-%m-%d", c)
                    use_time = str(use_time)
                    person_info['validTime'] = use_time
                except KeyError as e:
                    person_info['validTime'] = ''
                person_info['regNum'] = ''
                person_info['tokenKey'] = self.token

                print('非人员信息%s' % person_info)
                yield scrapy.FormRequest(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                    formdata=person_info,
                    callback=self.person_zz,
                    meta={'company_name': response.meta['company_name']},
                    dont_filter=True
                )
            else:
                # 岗位
                if i['positionCertInfos']:
                    print('我是%s--非注册人员--公司是%s---' % (i['name'], response.meta['company_name']))
                    try:
                        person_info['grade'] = i['positionCertInfos'][0]['positionType']['name']
                    except IndexError as e:
                        person_info['grade'] = ''

                    # 证书编号
                    try:
                        person_info['num'] = i['positionCertInfos'][0]['certificateNumber']
                    except IndexError as e:
                        person_info['num'] = ''
                    # 有效期
                    try:
                        # 有效期
                        c = time.localtime(int(i['positionCertInfos'][0]['expiryDt'] / 1000))
                        use_time = time.strftime("%Y-%m-%d", c)
                        use_time = str(use_time)
                        person_info['validTime'] = use_time
                    except KeyError as e:
                        person_info['validTime'] = ''
                    person_info['regNum'] = ''
                    person_info['major'] = ''
                    person_info['tokenKey'] = self.token
                    print('非人员信息%s' % person_info)
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_info,
                        callback=self.person_zz,
                        meta={'company_name': response.meta['company_name']},
                        dont_filter=True
                    )
                else:
                    person_info['grade'] = ''
                    person_info['major'] = ''
                    person_info['validTime'] = ''
                    person_info['num'] = ''
                    person_info['regNum'] = ''
                    person_info['tokenKey'] = self.token
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_info,
                        callback=self.person_zz,
                        meta={'company_name': response.meta['company_name']},
                        dont_filter=True
                    )

    def person_zz(self, response):
        not_company_code = json.loads(response.text)['code']
        not_search_company_name = response.meta['company_name']
        self.r.sadd('all_company_name', not_search_company_name)
        print(response.text)
        if not_company_code == -118:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_name3', not_search_company_name)
        else:
            print('当前人员添加完成')
