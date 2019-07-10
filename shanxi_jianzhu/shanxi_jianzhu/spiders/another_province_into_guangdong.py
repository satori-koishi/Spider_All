# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json



class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'another_province_into_guangdong'

    def start_requests(self):
        # pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        # self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://113.108.219.52/Dop/Open/IntoGDEnterpriseList.aspx'
        self.index = 1
        self.x = 1
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        # post_forama_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        # __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        # post_forama_data['__VIEWSTATE'] = __VIEWSTATE
        # post_forama_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        # post_forama_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        # post_forama_data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder$pGrid$nextpagebtn'
        # post_forama_data['ctl00$ContentPlaceHolder$ddlBussinessSystem'] = '39'

        tr = Selector(response=response).xpath('//table[@class="data-list"]/tr/td[1]/a/@href')
        for t in tr:
            tip = t.extract()
            print(tip)
            yield scrapy.Request(url=tip, callback=self.company_information)

        #                )
        # self.index = self.index + 1
        # if not self.index == 1596:
        #     yield scrapy.FormRequest(url=self.url,
        #                              formdata=post_forama_data,
        #                              callback=self.parse)

    def zz(self, response):
        print(response.text)

    def company_information(self, response):
        data = {}
        td = Selector(response=response).xpath('//div[@id="ent-info "]/div[2]/div/h5/text()').extract_first()
        company_name = Selector(response=response).xpath('//div[@class="ln-title"]/text()').extract_first()
        company_name = company_name.split()[0]
        data['companyName'] = company_name
        data['area'] = '广东省'
        data['companyArea'] = ''
        data['token'] = self.token
        number = td.split()
        if number != []:
            number = number[0]
            if len(number) != 18:
                data['licenseNum'] = ''
            else:
                data['licenseNum'] = number
        else:
            data['licenseNum'] = ''
        div_person = Selector(response=response).xpath('//div[@id="ent-into"]/div')
        # print(len(div_person),'sssssssssssssssssssss')
        if len(div_person) == 2:
            data['contactMan'] = ''
            data['contactAddress'] = ''
            data['contactPhone'] = ''
            print('无人员注入')
        else:
            address = div_person[3].xpath('./div/h5/text()').extract_first()
            person_name = div_person[4].xpath('./div/h5/text()').extract_first()
            phone_number = div_person[5].xpath('./div/h5/text()').extract_first()
            person_name = person_name.split()[0]
            address = address.split()[0]
            phone_number = phone_number.split()[0]
            data['contactMan'] = person_name
            data['contactAddress'] = address
            data['phone_number'] = phone_number
        print(data)
        return Request(url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                                    method="POST",
                                    headers={'Content-Type': 'application/json'},
                                    body=json.dumps(data),
                                    callback=self.zz
                      )
        # companyName = td[0].xpath('./td/text()').extract_first()
        # companyName = companyName.split()[0]
        # licenseNum = td[3].xpath('./td[3]/text()').extract_first()
        # if licenseNum.split() == None:
        #     licenseNum = ''
        # else:
        #     licenseNum = licenseNum.split()[0]
        # data['companyName'] = companyName
        # data['licenseNum'] = licenseNum
        # data['contactMan'] = ''
        # data['companyArea'] = '福建'
        # data['area'] = ''
        # data['contactAddress'] = ''
        # data['contactMan'] = ''
        # data['contactPhone'] = ''
        # data['token'] = self.token
        # print(data)
        # yield Request(url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
        #                             method="POST",
        #                             headers={'Content-Type': 'application/json'},
        #                             body=json.dumps(data),
        #                             callback=self.zz
        #               )



