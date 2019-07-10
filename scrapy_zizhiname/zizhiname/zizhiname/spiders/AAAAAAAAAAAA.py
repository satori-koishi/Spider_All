# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
from scrapy.http import Request
import json
import redis
from .. import items
import datetime
import time
import logging


class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    name = 'renyuan'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'

    def start_requests(self):
        person_document = {'companyName': '云南孟凯有限公司',
                           'name': 'kk',
                           'sex': '男',
                           'idType': '身份证',
                           'card': 'tttttttttttttt',
                           'grade': '高级工程师',
                           'major': '土木工程',
                           'num': '23123123123',
                           'sealNum': '陕213123',
                           'validTime': '2021-11-11',
                           'token': self.token
                           }
        yield Request(url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyEngineer.htm',
                      method="POST", body=json.dumps(person_document),
                      headers={'Content-Type': 'application/json'}, callback=self.zz)

    # 选择公司
    def zz(self, response):
        print(response.text)
