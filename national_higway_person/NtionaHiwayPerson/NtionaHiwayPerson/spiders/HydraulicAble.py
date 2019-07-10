# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import redis
import json
import re


class HydraulicAble(scrapy.Spider):
    name = 'HydraulicAble'

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
        company_name = Selector(response=response).xpath('//td[@colspan="3"]')[0].xpath('./a/@title').extract_first()
        number = Selector(response=response).xpath('//td[@colspan="3"]')[3].xpath(
            'text()').extract_first()
        if number.split():
            number = number.split()[0]
            if len(number) == 18:
                number = number
        else:
            number = ''

        ## 资质件信息
        ability_info_all = Selector(response=response).xpath('//table[@id="table_zz"]')
        if ability_info_all:
            ability_info_all = ability_info_all[0].xpath('./tbody/tr')
            for a in ability_info_all:
                info_condition = a.xpath('./td')
                ability_data = {'company_name': company_name, 'issuing_authority': '', 'ability_type': '',
                                'licence': '', 'grade': '', 'ability_number': '', 'start_date': ''}
                ability_type = info_condition[0].xpath('text()').extract_first()
                try:
                    ability_data['ability_type'] = ability_type.split()[0]

                except IndexError:
                    ability_data['ability_type'] = ''

                try:
                    licence = info_condition[1].xpath('text()').extract_first()
                    if licence is not None:
                        ability_data['licence'] = licence
                except IndexError:
                    pass

                try:
                    grade = info_condition[2].xpath('text()').extract_first()
                    if grade is not None:
                        ability_data['grade'] = grade
                except IndexError:
                    pass

                try:
                    ability_number = info_condition[3].xpath('text()').extract_first()
                    if ability_number is not None:
                        ability_data['ability_number'] = ability_number
                except IndexError:
                    continue

                try:
                    start_date = info_condition[4].xpath('text()').extract_first()
                    if start_date is not None:
                        ability_data['start_date'] = start_date
                except IndexError:
                    pass

                try:
                    end_date = info_condition[5].xpath('text()').extract_first()
                    if end_date is not None:
                        ability_data['end_date'] = end_date
                except IndexError:
                    pass

                try:
                    issuing_authority = info_condition[6].xpath('text()').extract_first()
                    if issuing_authority is not None:
                        ability_data['issuing_authority'] = issuing_authority
                except IndexError:
                    pass

                print('企业资质', ability_data,)
        #     # yield scrapy.FormRequest(url='tongna', formdata=ability_info_all, callback=self.ability_zz)

        # 安全证件信息
        ability_info_all2 = Selector(response=response).xpath('//table[@id="table_zz"]')
        if len(ability_info_all2) == 2:
            safe_ability = ability_info_all2[1].xpath('./tbody/tr')
            for s in safe_ability:
                safe_certificates_data = {'company_name': company_name, 'safe_number': '', 'address_certificates': '',
                                          'start_date_certificates': '', 'type_certificates': ''}
                all_safe_td = s.xpath('./td')
                safe_number = all_safe_td[0].xpath('text()').extract_first()
                if safe_number is not None:
                    safe_number = safe_number.split()[0]
                    if safe_number == '无':
                        continue
                    safe_certificates_data['safe_number'] = safe_number
                else:
                    continue

                address_certificates = all_safe_td[1].xpath('text()').extract_first()
                if address_certificates is not None:
                    safe_certificates_data['address_certificates'] = address_certificates

                start_date_certificates = all_safe_td[2].xpath('text()').extract_first()
                if start_date_certificates is not None:
                    safe_certificates_data['start_date_certificates'] = start_date_certificates

                type_certificates = all_safe_td[3].xpath('text()').extract_first()
                if type_certificates is not None:
                    safe_certificates_data['type_certificates'] = type_certificates
                print('企业安全证件信息', safe_certificates_data)
                    # yield scrapy.FormRequest(url='tongna', formdata=safe_certificates_data, callback=self.ability_zz)

        # 系统相关细信息
        authentication_all = Selector(response=response).xpath('//table[@id="table_sys"]')
        if authentication_all:
            authentica_tr = authentication_all.xpath('./tbody/tr')

            for a in authentica_tr:
                system_data = {'company_name': company_name, 'system_end': '', 'system_name': '',
                               'system_start': ''}
                d = a.xpath('./td')
                system_name = d[0].xpath('text()').extract_first()
                if system_name is not None:
                    # print('系统相关信息---%s----%s' % system_name, type(system_name))
                    system_data['system_name'] = system_name
                else:
                    continue

                system_start = d[1].xpath('text()').extract_first()
                if system_start is not None:
                    system_data['system_start'] = system_start

                system_end = d[2].xpath('text()').extract_first()
                if system_end is not None:
                    system_data['system_end'] = system_end
                print('企业系统认证', system_data)
        #         # yield scrapy.FormRequest(url='tongna', formdata=system_data, callback=self.ability_zz)



    def person_post(self, response):
        print(response)

    def ability_zz(self, response):
        print(response)
