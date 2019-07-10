# -*- coding: utf-8 -*-
import scrapy
import redis
import json


class HigWayPersonSpider(scrapy.Spider):
    name = 'HigWayPersonConstruction'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://glxy.mot.gov.cn/person/getPersonList.do'
        pool = redis.ConnectionPool(
            host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.start_formats = {'page': '1', 'rows': '15', 'type': '0'}

    def start_requests(self):
        yield scrapy.FormRequest(url=self.url,
                                 callback=self.parse,
                                 formdata=self.start_formats,
                                 )

    def parse(self, response):
        highways_data = {}
        data = json.loads(response.text)
        max_page = data['pageObj']['maxPage']
        print('当前页共%s---共有-%s页' % (len(data['rows']), max_page))
        for p in data['rows']:
            highways_data['companyName'] = p['company']
            highways_data['licenseNum'] = ''
            highways_data['birthDate'] = p['birthDate']
            highways_data['idType'] = p['idType']
            highways_data['idCard'] = p['idCard']
            highways_data['majorStartDate'] = p['majorStartDate']
            highways_data['name'] = p['name']
            highways_data['sex'] = p['sex']
            highways_data['status'] = p['status']
            highways_data['topCollege'] = p['topCollege']
            highways_data['topEducation'] = p['topEducation']
            highways_data['topMajor'] = p['topMajor']
            highways_data['address'] = p['address']
            highways_data['nation'] = p['nation']
            highways_data['engagedInSpecialty'] = p['engagedInSpecialty']
            highways_data['engagedYears'] = p['engagedyears']
            highways_data['companyYear'] = p['companyYear']
            highways_data['technicalTitle'] = p['technicalTitle']
            highways_data['professionalTitle'] = p['professionalTitle']
            if p['jobResume'] == '':
                highways_data['jobResume'] = ''
            else:
                highways_data['jobResume'] = p['jobResume'].split()[0]
            highways_data['tokenKey'] = self.token
            print(highways_data)
            yield scrapy.FormRequest(url='https://api.maotouin.com/rest/companyInfo/addRoadCompanyEngineer.htm',
                                     formdata=highways_data,
                                     callback=self.person_post,
                                     dont_filter=True,
                                     meta={'company_name': p['company'],
                                           'name': p['name']
                                           },
                                     )
        page = int(self.start_formats['page'])
        max_page = data['pageObj']['maxPage']
        page += 1
        if page != (max_page + 1):
            self.start_formats['page'] = str(page)
            yield scrapy.FormRequest(url=response.url,
                                     formdata=self.start_formats,
                                     callback=self.parse,
                                     )

    def person_post(self, response):
        not_company_code = json.loads(response.text)['code']
        print(response.text, response.meta['company_name'])
        if not_company_code == -118 or not_company_code == -102:
            self.r.sadd('title_name1', response.meta['company_name'])
            self.r.sadd('title_name3', response.meta['company_name'])
            print('当前公司不存在已经正在添加')
        else:
            print(response.meta['name'], '添加成功')
