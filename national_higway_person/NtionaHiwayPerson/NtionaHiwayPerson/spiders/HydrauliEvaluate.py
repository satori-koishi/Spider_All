# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import redis
import json
import re


class HydraulicEvaluate(scrapy.Spider):
    name = 'HydraulicEvaluate'

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

        tr = Selector(response=response).xpath('//table[@id="table_credit"]/tbody/tr')
        just_z = Selector(response=response).xpath('//table[@id="table_credit"]/tbody/tr[1]/td[1]/text()').extract_first()
        if just_z != '没有相关数据':
            for t in tr:
                credit_evaluate = {'type_name': '', 'e_result': '',
                                   'have_date': '', 'department': '',
                                   'validity_time': '', 'company_name': company_name,
                                   'number': number
                                   }
                # 类别
                type_name = t.xpath('./td/text()')[0].extract().split()[0]
                credit_evaluate['type_name'] = type_name

                # 评价结果
                e_result = t.xpath('./td/text()')[1].extract()
                if e_result is not None:
                    credit_evaluate['e_result'] = e_result

                # 颁发日期
                have_date = t.xpath('./td/text()')[2].extract()
                if have_date is not None:
                    credit_evaluate['have_date'] = have_date

                # 评价机构
                department = t.xpath('./td/text()')[3].extract()
                if department is not None:
                    credit_evaluate['department'] = department

                # 有效期
                validity_time = t.xpath('./td/text()')[4].extract()
                if validity_time is not None:
                    credit_evaluate['validity_time'] = validity_time

                print(credit_evaluate)

    def person_post(self, response):
        print(response)

    def ability_zz(self, response):
        print(response)
