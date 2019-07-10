# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import redis
import json
import re


class HydraulicEngineer(scrapy.Spider):
    name = 'HydraulicEngineer'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://xypt.mwr.gov.cn/UnitCreInfo/listCyryPage.do?'
        # pool = redis.ConnectionPool(
        #     host='106.12.112.205', password='tongna888')
        # self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.index = 1
        self.flag = True

    def start_requests(self):
        yield scrapy.Request(url=self.url + 'TYPE=1',
                             callback=self.parse,
                             )

    def parse(self, response):
        # print(response.text)
        if self.flag:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[6].xpath('./a/@onclick')\
                .extract_first()
            self.flag = False
        else:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[8].xpath('./a/@onclick') \
                .extract_first()
        page = re.findall('nextPage\((\d+)\)', page)[0]
        page = int(page) + 1
        print(page, 'page')
        person_url = Selector(response=response).xpath('//a[@style="color: blue"]/@href')
        for p in person_url:
            zz = p.extract()
            url = re.findall('javascript:toChangeTop\(\'cyry\'\);menuJump\(\'(.*)\'\)', zz)[0]
            yield scrapy.Request(url=url, callback=self.person_info)
        self.index += 1
        if page != self.index:
            yield scrapy.Request(url=self.url + 'currentPage=%s&showCount=20' % self.index,
                                 callback=self.parse,
                                 )

    def zz(self, response):
        print(response.text)

    def person_info(self, response):
        data = {'duty': '', 'occupational_name': '', 'word_date': '', 'job_name': '', 'number': '',
                'registration_number': '', 'major': '', 'Certification': '', 'Remarks': '', 'validity': ''
                }

        name = Selector(response=response).xpath('//table[@id="table_report"]/tr[1]/td[2]/text()').extract_first()
        data['name'] = name

        sxe = Selector(response=response).xpath('//table[@id="table_report"]/tr[1]/td[4]/text()').extract_first()
        data['sxe'] = sxe

        company_name = Selector(response=response).\
            xpath('//table[@id="table_report"]/tr[2]/td[2]/text()').extract_first()
        data['company_name'] = company_name

        title = Selector(response=response).xpath('//table[@id="table_report"]/tr[3]/td[2]/text()').extract_first()
        data['title'] = title

        card = Selector(response=response).xpath('//table[@id="table_report"]/tr[3]/td[4]/text()').extract_first()
        data['card'] = card

        duty = Selector(response=response).xpath('//table[@id="table_report"]/tr[4]/td[2]/text()').extract_first()
        if duty is not None:
            data['duty'] = duty

        occupational_name = Selector(response=response)\
            .xpath('//table[@id="table_report"]/tr[4]/td[4]/text()').extract_first()
        if occupational_name is not None:
            data['occupational_name'] = occupational_name

        word_date = Selector(response=response).xpath('//table[@id="table_report"]/tr[5]/td[2]/text()').extract_first()
        if word_date is not None:
            data['word_date'] = word_date

        certificate_info = Selector(response=response).xpath('//table[@id="table_zcxx"]/tbody/tr')
        print(len(certificate_info))
        if len(certificate_info) != 0:
            for c in certificate_info:
                each_certificate = c.xpath('./td')
                job_name = each_certificate[0].xpath('text()').extract_first()
                if job_name is not None:
                    data['job_name'] = job_name
                number = each_certificate[1].xpath('text()').extract_first()
                if number is not None:
                    data['number'] = number
                registration_number = each_certificate[2].xpath('text()').extract_first()
                if registration_number is not None:
                    data['registration_number'] = registration_number
                major = each_certificate[3].xpath('text()').extract_first()
                if major is not None:
                    data['major'] = major
                validity = each_certificate[4].xpath('text()').extract_first()
                if validity is not None:
                    data['validity'] = validity
                certification = each_certificate[5].xpath('text()').extract_first()
                if certification is not None:
                    data['Certification'] = certification
                remarks = each_certificate[6].xpath('text()').extract_first()
                if remarks is not None:
                    data['Remarks'] = remarks

                print(len(each_certificate), data, '每一条证件信息')
                # yield scrapy.FormRequest(url='tongna', formdata=data, callback=self.person_post)
        else:
            print(len(certificate_info), data, '没有证件信息')
            # yield scrapy.FormRequest(url='tongna', formdata=data, callback=self.person_post)

    def person_post(self, response):
        print(response)