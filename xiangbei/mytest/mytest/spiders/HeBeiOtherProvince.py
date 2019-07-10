# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import json
import re


class HeBeiOtherProvince(scrapy.Spider):
    name = 'HeBeiOtherProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://zfcxjst.hebei.gov.cn/was5/web/search?channelid=204700'
        self.flag = True
        self.index = 1
        self.number = 20
        self.data = {'area': '河北省', 'companyArea': '', 'contactAddress': '', 'contactPhone': '', 'token': self.token}

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        page = Selector(response=response).xpath('//a[@class="last-page"]/@href').extract_first()
        cc = 'search\?page=(\d+)\&channelid=204700\&perpage=15\&outlinepage=10\&zsbh=\&Applyname='
        info_page = int(re.findall(cc, page)[0])
        print(info_page, 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        last_page = 'http://zfcxjst.hebei.gov.cn/was5/web/detail?record=%s&channelid=204700' % (
            info_page)
        print(info_page, 'xxxxxxxxxxxxxxxxxxxxxxx')
        yield scrapy.Request(
            url=last_page,
            callback=self.parse,
            meta={'page': info_page}
        )

    def parse(self, response):
        company_name = Selector(response).xpath('//table[@align="center"]/tr[3]/td[2]/text()').extract_first()
        if company_name is not None:
            repeat = self.r.sadd('Company_name', company_name + '河北省')
            if repeat:
                number = Selector(response).xpath('//table[@align="center"]/tr[4]/td[2]/text()').extract_first()
                self.data['companyName'] = company_name
                if number is not None:
                    if len(number) != 18:
                        self.data['licenseNum'] = ''
                    else:
                        self.data['licenseNum'] = number
                else:
                    self.data['licenseNum'] = ''
                div_table = Selector(response=response).xpath('//td[@colspan="4"]')[6]
                contactMan = div_table.xpath('text()').extract_first()
                if contactMan is not None:
                    self.data['contactMan'] = contactMan
                else:
                    self.data['contactMan'] = ''
                print(self.data)
                yield scrapy.FormRequest(url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                                         method="POST",
                                         headers={'Content-Type': 'application/json'},
                                         body=json.dumps(self.data),
                                         callback=self.zz,
                                         meta={'company_name': company_name, 'data': self.data})
            else:
                print('此公司信息已经存在', company_name)

        print(response.meta['page'], type(response.meta['page']))
        page = int(response.meta['page'])
        page -= 1
        self.number -= 1
        if page != 0:
            url = 'http://zfcxjst.hebei.gov.cn/was5/web/detail?record=%s&channelid=204700' % page
            yield scrapy.Request(url=url, callback=self.parse, meta={'page': page})

    def zz(self, response):
        not_company_code = json.loads(response.text)['code']
        not_search_company_name = response.meta['company_name']
        zz_data = response.meta['data']
        self.r.sadd('all_company_name', not_search_company_name)
        print(response.text)
        data = json.dumps(zz_data, ensure_ascii=False)
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')