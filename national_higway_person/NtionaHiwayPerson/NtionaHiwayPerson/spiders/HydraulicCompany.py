# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import redis
import json
import re


class HydraulicCompany(scrapy.Spider):
    name = 'HydraulicCompany'

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
        # company_data = {'unit_type': response.meta['unit_type'], 'city': '',
        #                 'start_date': '', 'number': '', 'authority': '', 'type_of_registration': '',
        #                 'business_area': '', 'security_number': '', 'capital': '', 'unit_property': '',
        #                 'social_registration': '', 'registered_address': '', 'registered__postal_code': '',
        #                 'business_address': '', 'business_postal_number': '', 'legal_person': '',
        #                 'website': '',
        #                 }
        company_name = Selector(response=response).xpath('//td[@colspan="3"]')[0].xpath('./a/@title').extract_first()
            # company_data['company_name'] = company_name
        # # test = self.r.sadd('title_name1', company_name)
        # unit_property = Selector(response=response).xpath(
        #     '//td[@style="width: 350px;padding-top: 9px;"]/text()').extract_first()
        # if unit_property.split():
        #     unit_property = unit_property.split()[0]
        #     company_data['unit_property'] = unit_property
        #
        # capital = Selector(response=response).xpath('//td[@colspan="3"]')[2].xpath('text()').extract_first()
        # if capital is not None:
        #     if capital != '/':
        #         company_data['capital'] = capital + '万元'
        #
        # city = Selector(response=response).xpath('//td[@colspan="3"]')[1].xpath('text()').extract_first()
        # if city.split():
        #     city = city.split()[0]
        #     company_data['city'] = city
        #
        # start_company_data = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[
        #     3].xpath('text()').extract_first()
        # if start_company_data.split():
        #     start_company_data = start_company_data.split()[0]
        #     company_data['start_date'] = start_company_data
        #
        # number = Selector(response=response).xpath('//td[@colspan="3"]')[3].xpath(
        #     'text()').extract_first()
        # if number.split():
        #     number = number.split()[0]
        #     company_data['number'] = number
        #
        # authority = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[5].xpath(
        #     'text()').extract_first()
        # if authority is not None:
        #     authority = authority.split()[0]
        #     if authority != '/':
        #         company_data['authority'] = authority
        #
        # type_of_registration = Selector(response=response).xpath('//td[@colspan="5"]')[0].xpath(
        #     'text()').extract_first()
        # if type_of_registration.split():
        #     type_of_registration = type_of_registration.split()[0]
        #     company_data['type_of_registration'] = type_of_registration
        #
        # business_area = Selector(response=response).xpath('//td[@colspan="5"]')[1].xpath(
        #     'text()').extract_first()
        # if business_area is not None:
        #     business_area = business_area.split()[0]
        #     if business_area != '/':
        #         company_data['business_area'] = business_area
        #
        # security_number = Selector(response=response).xpath('//td[@colspan="3"]')[4].xpath(
        #     'text()').extract_first()
        # if security_number is not None:
        #     security_number = security_number.split()[0]
        #     if security_number != '/':
        #         company_data['security_number'] = security_number
        #
        # social_registration = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[
        #     9].xpath(
        #     'text()').extract_first()
        # if social_registration is not None:
        #     social_registration = social_registration.split()[0]
        #     if social_registration != '/':
        #         company_data['social_registration'] = social_registration
        #
        # registered_address = Selector(response=response).xpath('//td[@colspan="3"]')[5].xpath(
        #     'text()').extract_first()
        # if registered_address is not None:
        #     registered_address = registered_address.split()[0]
        #     if registered_address != '/':
        #         company_data['registered_address'] = registered_address
        #
        # registered__postal_code = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[
        #     11].xpath(
        #     'text()').extract_first()
        # if registered__postal_code is not None:
        #     registered__postal_code = registered__postal_code.split()[0]
        #     if registered__postal_code != '/':
        #         company_data['registered__postal_code'] = registered__postal_code
        #
        # business_address = Selector(response=response).xpath('//td[@colspan="3"]')[5].xpath(
        #     'text()').extract_first()
        # if business_address is not None:
        #     business_address = business_address.split()[0]
        #     if business_address != '/':
        #         company_data['business_address'] = business_address
        #
        # business_postal_number = Selector(response=response).xpath('//td[@style="width: 230px;padding-top: 9px;"]')[
        #     13].xpath(
        #     'text()').extract_first()
        # if business_postal_number is not None:
        #     business_postal_number = business_postal_number.split()[0]
        #     if business_postal_number != '/':
        #         company_data['business_postal_number'] = business_postal_number
        #
        # legal_person = Selector(response=response).xpath('//td[@colspan="2"]/text()').extract_first()
        # if legal_person is not None:
        #     legal_person = legal_person.split()[0]
        #     if legal_person != '/':
        #         company_data['legal_person'] = legal_person
        #
        # if len(Selector(response=response).xpath('//td[@colspan="5"]')) == 3:
        #     website = Selector(response=response).xpath('//td[@colspan="5"]')[2].xpath(
        #         'text()').extract_first()
        #     if website.split():
        #         print(website.split(), 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        #         website = website.split()[0]
        #         if website.startswith('www') or website.startswith('http'):
        #             company_data['website'] = website
        #     print('公司信息', company_data)
        # yield scrapy.FormRequest(url='tongna', formcompany_data=company_data, callback=self.company_zz)

        ## 资质件信息
        # ability_info_all = Selector(response=response).xpath('//table[@id="table_zz"]')
        # # print(ability_info_all, company_name)
        # if ability_info_all:
        #     ability_info_all = ability_info_all[0].xpath('./tbody/tr')
        #     for a in ability_info_all:
        #         info_condition = a.xpath('./td')
        #         # print(len(info_condition), company_name)
        #         ability_data = {'company_name': company_name, 'issuing_authority': '', 'ability_type': '',
        #                         'licence': '', 'grade': '', 'ability_number': '', 'start_date': ''}
        #         ability_type = info_condition[0].xpath('text()').extract_first()
        #         try:
        #             ability_data['ability_type'] = ability_type.split()[0]
        #
        #         except IndexError:
        #             ability_data['ability_type'] = ''
        #
        #         try:
        #             licence = info_condition[1].xpath('text()').extract_first()
        #             if licence is not None:
        #                 ability_data['licence'] = licence
        #         except IndexError:
        #             pass
        #
        #         try:
        #             grade = info_condition[2].xpath('text()').extract_first()
        #             if grade is not None:
        #                 ability_data['grade'] = grade
        #         except IndexError:
        #             pass
        #
        #         try:
        #             ability_number = info_condition[3].xpath('text()').extract_first()
        #             if ability_number is not None:
        #                 ability_data['ability_number'] = ability_number
        #         except IndexError:
        #             continue
        #
        #         try:
        #             start_date = info_condition[4].xpath('text()').extract_first()
        #             if start_date is not None:
        #                 ability_data['start_date'] = start_date
        #         except IndexError:
        #             pass
        #
        #         try:
        #             end_date = info_condition[5].xpath('text()').extract_first()
        #             if end_date is not None:
        #                 ability_data['end_date'] = end_date
        #         except IndexError:
        #             pass
        #
        #         try:
        #             issuing_authority = info_condition[6].xpath('text()').extract_first()
        #             if issuing_authority is not None:
        #                 ability_data['issuing_authority'] = issuing_authority
        #         except IndexError:
        #             pass
        #
        #         print('企业资质', ability_data, 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        # #     # yield scrapy.FormRequest(url='tongna', formdata=ability_info_all, callback=self.ability_zz)

        ## 安全证件信息
        # ability_info_all2 = Selector(response=response).xpath('//table[@id="table_zz"]')
        # if len(ability_info_all2) == 2:
        #     safe_ability = ability_info_all2[1].xpath('./tbody/tr')
        #     print('为啥不执行这个安全证件信息？？？？%s' % safe_ability)
        #     for s in safe_ability:
        #         safe_certificates_data = {'company_name': company_name, 'safe_number': '', 'address_certificates': '',
        #                                   'start_date_certificates': '', 'type_certificates': ''}
        #         all_safe_td = s.xpath('./td')
        #         safe_number = all_safe_td[0].xpath('text()').extract_first()
        #         if safe_number is not None:
        #             safe_number = safe_number.split()[0]
        #             if safe_number == '无':
        #                 continue
        #             safe_certificates_data['safe_number'] = safe_number
        #         else:
        #             continue
        #
        #         address_certificates = all_safe_td[1].xpath('text()').extract_first()
        #         if address_certificates is not None:
        #             safe_certificates_data['address_certificates'] = address_certificates
        #
        #         start_date_certificates = all_safe_td[2].xpath('text()').extract_first()
        #         if start_date_certificates is not None:
        #             safe_certificates_data['start_date_certificates'] = start_date_certificates
        #
        #         type_certificates = all_safe_td[3].xpath('text()').extract_first()
        #         if type_certificates is not None:
        #             safe_certificates_data['type_certificates'] = type_certificates
        #         print('企业安全证件信息', safe_certificates_data, 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
        #             # yield scrapy.FormRequest(url='tongna', formdata=safe_certificates_data, callback=self.ability_zz)
        #
        ## 系统相关细信息
        # authentication_all = Selector(response=response).xpath('//table[@id="table_sys"]')
        # if authentication_all:
        #     authentica_tr = authentication_all.xpath('./tbody/tr')
        #
        #     for a in authentica_tr:
        #         system_data = {'company_name': company_name, 'system_end': '', 'system_name': '',
        #                        'system_start': ''}
        #         d = a.xpath('./td')
        #         system_name = d[0].xpath('text()').extract_first()
        #         if system_name is not None:
        #             # print('系统相关信息---%s----%s' % system_name, type(system_name))
        #             system_data['system_name'] = system_name
        #         else:
        #             continue
        #
        #         system_start = d[1].xpath('text()').extract_first()
        #         if system_start is not None:
        #             # print('系统相关信息---%s----%s' % system_start, type(system_start))
        #             system_data['system_start'] = system_start
        #
        #         system_end = d[2].xpath('text()').extract_first()
        #         if system_end is not None:
        #             # print('系统相关信息---%s----%s' % system_end, type(system_end))
        #             system_data['system_end'] = system_end
        #         print('企业系统认证', system_data, 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC')
        # #         # yield scrapy.FormRequest(url='tongna', formdata=system_data, callback=self.ability_zz)

        # 项目详情
        project_performance = Selector(response=response).xpath('//div[@id="tab4"]/table/tbody/tr')
        print(len(project_performance), project_performance.xpath('./td/text()').extract_first(), company_name)
        if len(project_performance) != 1:
            for p in project_performance:
                project_data = {'project_name': '', 'project_address': '', 'project_status': '', 'project_capital': '',
                                'project_start_date': '', 'project_company': '', 'project_complete': ''}
                easy_info = p.xpath('./td[@align="center"]')
                if len(easy_info) == 0:
                    pass
                else:
                    print(len(easy_info), 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    project_name = easy_info[2].xpath('text()').extract_first()
                    if project_name is not None:
                        project_data['project_name'] = project_name
                    else:
                        continue

                    project_address = easy_info[3].xpath('text()').extract_first()
                    if project_address is not None:
                        project_data['project_address'] = project_address

                    project_status = easy_info[4].xpath('text()').extract_first()
                    if project_status is not None:
                        project_data['project_status'] = project_status

                    project_capital = easy_info[5].xpath('text()').extract_first()
                    if project_capital is not None:
                        project_data['project_capital'] = project_capital

                    project_start_date = easy_info[6].xpath('text()').extract_first()
                    if project_start_date is not None:
                        project_data['project_start_date'] = project_start_date

                    project_company = easy_info[7].xpath('text()').extract_first()
                    if project_company is not None:
                        project_data['project_company'] = project_company

                    project_complete = easy_info[8].xpath('./font/text()').extract_first()
                    if project_complete is not None:
                            project_data['project_complete'] = project_complete
                content = p.xpath('./td[@colspan="9"]/table[@id="table_report"]/tr')



                print(project_data)



    def person_post(self, response):
        print(response)

    def ability_zz(self, response):
        print(response)
