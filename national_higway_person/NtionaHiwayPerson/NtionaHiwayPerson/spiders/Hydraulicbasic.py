# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import redis
import json
import re


class HydraulicBasic(scrapy.Spider):
    name = 'HydraulicBasic'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://xypt.mwr.gov.cn/UnitCreInfo/listCydwPage.do?'
        pool = redis.ConnectionPool(
            host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.index = 1
        self.flag = True

    def start_requests(self):
        yield scrapy.Request(url=self.url + 'currentPage=1&showCount=20',
                             callback=self.parse,
                             )

    def parse(self, response):
        # print(response.text)
        if self.flag:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[6].xpath('./a/@onclick') \
                .extract_first()
            self.flag = False
        else:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[8].xpath('./a/@onclick') \
                .extract_first()
        page = re.findall('nextPage\((\d+)\)', page)[0]
        page = int(page) + 1
        print(page, 'page')
        person_url = Selector(response=response).xpath('//table[@id="example-advanced"]/tbody/tr')
        for p in person_url:
            zz = p.xpath('./td[2]/a/@href').extract_first()
            unit_type = p.xpath('./td[3]/text()').extract_first()
            if unit_type is None:
                unit_type = ''
            a = re.findall('javascript:toChangeTop\(\'(.*)\'\);toDetail\(\'(.*)\'\)', zz)
            yield scrapy.Request(url='http://xypt.mwr.gov.cn/UnitCreInfo/frontunitInfoList.do?ID=%s&menu=%s'
                                     % (a[0][1], a[0][0]),
                                 callback=self.company_info,
                                 meta={'unit_type': unit_type}
                                 )
        self.index += 1
        if page != self.index:
            yield scrapy.Request(url=self.url + 'currentPage=%s&showCount=20' % self.index,
                                 callback=self.parse,
                                 )

    def company_zz(self, response):
        print(response.text)

    def company_info(self, response):
        company_data = {'unit_type': response.meta['unit_type'], 'city': '',
                        'start_date': '', 'number': '', 'authority': '', 'type_of_registration': '',
                        'business_area': '', 'security_number': '', 'capital': '', 'unit_property': '',
                        'social_registration': '', 'registered_address': '', 'registered__postal_code': '',
                        'business_address': '', 'business_postal_number': '', 'legal_person': '',
                        'website': '',
                        }
        company_name = Selector(response=response).xpath('//td[@colspan="3"]')[0].xpath('./a/@title').extract_first()
        company_data['company_name'] = company_name

        # yield scrapy.FormRequest()

        # test = self.r.sadd('title_name1', company_name)
        unit_property = Selector(response=response).xpath(
            '//td[@style="width: 350px;padding-top: 9px;"]/text()').extract_first()
        if unit_property.split():
            unit_property = unit_property.split()[0]
            company_data['unit_property'] = unit_property

        capital = Selector(response=response).xpath('//td[@colspan="3"]')[2].xpath('text()').extract_first()
        if capital is not None:
            if capital != '/':
                company_data['capital'] = capital + '万元'

        city = Selector(response=response).xpath('//td[@colspan="3"]')[1].xpath('text()').extract_first()
        if city.split():
            city = city.split()[0]
            company_data['city'] = city

        start_company_data = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[
            3].xpath('text()').extract_first()
        if start_company_data.split():
            start_company_data = start_company_data.split()[0]
            company_data['start_date'] = start_company_data

        number = Selector(response=response).xpath('//td[@colspan="3"]')[3].xpath(
            'text()').extract_first()
        if number.split():
            number = number.split()[0]
            if len(number) == 18:
                company_data['number'] = number

        authority = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[5].xpath(
            'text()').extract_first()
        if authority is not None:
            authority = authority.split()[0]
            if authority != '/':
                company_data['authority'] = authority

        type_of_registration = Selector(response=response).xpath('//td[@colspan="5"]')[0].xpath(
            'text()').extract_first()
        if type_of_registration.split():
            type_of_registration = type_of_registration.split()[0]
            company_data['type_of_registration'] = type_of_registration

        business_area = Selector(response=response).xpath('//td[@colspan="5"]')[1].xpath(
            'text()').extract_first()
        if business_area is not None:
            business_area = business_area.split()[0]
            if business_area != '/':
                company_data['business_area'] = business_area

        security_number = Selector(response=response).xpath('//td[@colspan="3"]')[4].xpath(
            'text()').extract_first()
        if security_number is not None:
            security_number = security_number.split()[0]
            if security_number != '/':
                company_data['security_number'] = security_number

        social_registration = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[
            9].xpath(
            'text()').extract_first()
        if social_registration is not None:
            social_registration = social_registration.split()[0]
            if social_registration != '/':
                company_data['social_registration'] = social_registration

        registered_address = Selector(response=response).xpath('//td[@colspan="3"]')[5].xpath(
            'text()').extract_first()
        if registered_address is not None:
            registered_address = registered_address.split()[0]
            if registered_address != '/':
                company_data['registered_address'] = registered_address

        registered__postal_code = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[
            11].xpath(
            'text()').extract_first()
        if registered__postal_code is not None:
            registered__postal_code = registered__postal_code.split()[0]
            if registered__postal_code != '/':
                company_data['registered__postal_code'] = registered__postal_code

        business_address = Selector(response=response).xpath('//td[@colspan="3"]')[5].xpath(
            'text()').extract_first()
        if business_address is not None:
            business_address = business_address.split()[0]
            if business_address != '/':
                company_data['business_address'] = business_address

        business_postal_number = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[
            13].xpath(
            'text()').extract_first()
        if business_postal_number is not None:
            business_postal_number = business_postal_number.split()[0]
            if business_postal_number != '/':
                company_data['business_postal_number'] = business_postal_number

        legal_person = Selector(response=response).xpath('//td[@colspan="2"]/text()').extract_first()
        if legal_person is not None:
            legal_person = legal_person.split()[0]
            if legal_person != '/':
                company_data['legal_person'] = legal_person

        if len(Selector(response=response).xpath('//td[@colspan="5"]')) == 3:
            website = Selector(response=response).xpath('//td[@colspan="5"]')[2].xpath(
                'text()').extract_first()
            if website.split():
                print(website.split(), 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                website = website.split()[0]
                if website.startswith('www') or website.startswith('http'):
                    company_data['website'] = website
        print('公司信息', company_data)
        # yield scrapy.FormRequest(url='tongna', formcompany_data=company_data, callback=self.company_zz)

    def company_zz(self, response):
        print(response)

