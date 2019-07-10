# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import time
import json
import re
from lxml import etree


class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'another_into_jilin'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.data = {'area': '吉林省', 'companyArea': ''}
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        now_time = time.time() * 1000 - 1000000
        self.index = 1
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data['token'] = self.token
        self.bigurl = 'http://cx.jlsjsxxw.com/'
        self.url = 'http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SwCorpData' \
                   '&nPageIndex=%s' \
                   '&nPageCount=127' \
                   '&nPageRowsCount=2527' \
                   '&nPageSize=%s' \
                   '&_=%s' % (1, 20, now_time)
        self.province_flag = True
        self.province = 1

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        zz = Selector(response=response).xpath('//tr/td[2]/a')
        print(len(zz))
        for z in zz:
            url = z.xpath('@href').extract_first()
            url = url.split(r'\"')[1]
            url = url.split('..')[1]
            xx = '/CorpInfo/CorpSwDetailInfo.aspx\?rowGuid=(.*)\&corpid=(.*)\&VType=\d+\&CertType=\d+'
            cc = re.findall(xx, url)
            company_name = z.xpath('text()').extract_first()
            print(self.bigurl + url, 'vvvvvvvvvvvvvvvvvvvvvvvvv')
            # yield scrapy.Request(url=self.bigurl + url, callback=self.company_information,
            #                      meta={'cc': cc}
            #                      )
            yield scrapy.Request(url='http://cx.jlsjsxxw.com/handle/Company_OutDetails'
                                     '_CertifiedEngineers.ashx?corpid=%s'
                                     '&ReocrdGuid=%s&_=1556177544518' % (cc[0][1], cc[0][0]),
                                 callback=self.person_info,
                                 meta={'company_name': company_name},
                                 dont_filter=True
                                 )
            yield scrapy.Request(url='http://cx.jlsjsxxw.com/handle/Company_OutDetails_PositionUser'
                                     '.ashx?corpid=%s'
                                     '&ReocrdGuid=%s&_=1556177544518' % (cc[0][1], cc[0][0]),
                                 callback=self.person_info,
                                 meta={'company_name': company_name},
                                 dont_filter=True
                                 )
            yield scrapy.Request(url='http://cx.jlsjsxxw.com/handle/Company_OutDetails_TechTitleUser'
                                     '.ashx?corpid=%s'
                                     '&ReocrdGuid=%s&_=1556177544518' % (cc[0][1], cc[0][0]),
                                 callback=self.person_info,
                                 meta={'company_name': company_name},
                                 dont_filter=True
                                 )

        self.index = self.index + 1
        if self.index != 130:
                print('当前第%s多少页' % self.index)
                now_time = time.time() * 1000 - 1000000
                yield scrapy.Request(url='http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SwCorpData&CorpName=&AptitudeNum=&TradeID=&BoundID=&LevelID=&ProvinceNum=&nPageIndex=%s&nPageCount=126&nPageRowsCount=2516&nPageSize=20&_=%s' % (self.index, now_time), callback=self.parse)

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@class="name_level3"]')[0].xpath('text()').extract_first()
        number = Selector(response=response).xpath('//td[@id="Td3"]/text()').extract_first()
        person = Selector(response=response).xpath('//td[@id="EconType"]/text()').extract_first()
        address = Selector(response=response).xpath('//td[@id="LicenseNum"]/text()').extract_first()
        phone = Selector(response=response).xpath('//td[@id="RegPrin"]/text()').extract_first()
        company_name = company_name.split()[0]
        if phone is None:
            self.data['contactPhone'] = ''
        else:
            phone = phone.split()
            phone = phone[0]
            if phone == '/':
                self.data['contactPhone'] = ''
            else:
                self.data['contactPhone'] = phone
        if person is None:
            self.data['contactMan'] = ''
        else:
            person = person.split()
            person = person[0]
            self.data['contactMan'] = person
        if address is None:
            self.data['contactAddress'] = ''
        else:
            address = address.split()
            address = address[0]
            self.data['contactAddress'] = address
        if number is not None:
            number = number.split()
            number = number[0]
            if len(number) != 18:
                self.data['licenseNum'] = ''
            else:
                self.data['licenseNum'] = number
        else:
            self.data['licenseNum'] = ''
        self.data['companyName'] = company_name
        # print(self.data)
        yield scrapy.Request(
            url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
            # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
            method="POST",
            headers={'Content-Type': 'application/json'},
            body=json.dumps(self.data),
            callback=self.zz,
            meta={'company_name': company_name, 'data': self.data}
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
        # print(response.body.decode(), type(response), dir(response))
        person_zz = json.loads(response.text)
        person_every = dict(person_zz)
        html_tr = etree.HTML(person_every['tb'])
        result = etree.tostring(html_tr)
        tr = html_tr.xpath("//tr")
        if person_every['Title'] == '注册人员':
            for t in tr:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': '', 'name': '', 'area': '吉林省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                               'validTime': '', 'tel': '', 'tokenKey': self.token
                               }
                if t.xpath('./td/text()')[0] != '没有数据':
                    name = t.xpath('./td[@class="align_center orange_name"]/text()')
                    print(name)
                    if name:
                        person_data['name'] = name[0]

                    num = t.xpath('./td[@class="align_center"]')[1].xpath('text()')
                    if num:
                        person_data['num'] = num[0]
                    else:
                        continue

                    major = t.xpath('./td[@class="align_center"]')[2].xpath('text()')
                    print(major, 'aaaaaaaaaaaaaaaa')
                    if major:
                        if major != '();':
                            person_data['major'] = major[0]

                    grade = t.xpath('./td[@class="align_center"]')[3].xpath('text()')
                    if grade:
                        person_data['grade'] = grade[0]

                    validTime = t.xpath('./td[@class="align_center"]')[4].xpath('text()')
                    if validTime:
                        person_data['validTime'] = validTime[0]

                    id_card = t.xpath('./td[@class="align_center"]')[7].xpath('text()')
                    if id_card:
                        person_data['idCard'] = id_card[0]
                    print(person_data,'AAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': response.meta['company_name']},
                        dont_filter=True,
                    )

        elif person_every['Title'] == '现场管理人员':
            for t in tr:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': '', 'name': '', 'area': '吉林省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                               'validTime': '', 'tel': '', 'tokenKey': self.token
                               }
                if t.xpath('./td/text()')[0] != '没有数据':
                    name = t.xpath('./td[@class="align_center orange_name"]/text()')
                    if name:
                        person_data['name'] = name[0]
                    number = t.xpath('./td[@class="align_center"]')[1].xpath('text()')
                    if number:
                        person_data['num'] = name[0]

                    grade = t.xpath('./td[@class="align_center"]')[2].xpath('text()')
                    if grade:
                        person_data['grade'] = grade[0]

                    id_card = t.xpath('./td[@class="align_center"]')[3].xpath('text()')
                    if id_card:
                        person_data['idCard'] = id_card[0]

                    print(person_data, '现场管理人员')
                    yield scrapy.FormRequest(
                        url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm',
                        formdata=person_data,
                        callback=self.person_post,
                        meta={'data': person_data, 'company_name': response.meta['company_name']},
                        dont_filter=True,
                    )

        elif person_every['Title'] == '职称人员':
            for t in tr:
                person_data = {'companyName': response.meta['company_name'],
                               'licenseNum': '', 'name': '', 'area': '吉林省', 'sex': '',
                               'idCard': '', 'grade': '', 'major': '', 'num': '', 'regNum': '',
                               'validTime': '', 'tel': '', 'tokenKey': self.token
                               }
                if t.xpath('./td/text()')[0] != '没有数据':
                    name = t.xpath('./td[@class="align_center orange_name"]/text()')
                    if name:
                        person_data['name'] = name[0]
                    grade = t.xpath('./td[@class="align_center"]')[1].xpath('text()')
                    if grade:
                        person_data['grade'] = grade[0]

                    major = t.xpath('./td[@class="align_center"]')[2].xpath('text()')
                    if major:
                        person_data['major'] = major[0]

                    id_card = t.xpath('./td[@class="align_center"]')[3].xpath('text()')
                    if id_card:
                        person_data['idCard'] = id_card[0]
                    print(person_data, '职称人员------------')
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