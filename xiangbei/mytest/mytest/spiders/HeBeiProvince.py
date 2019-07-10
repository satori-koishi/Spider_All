# -*- coding: utf-8 -*-
import scrapy
import json
import redis
from scrapy import Selector
from scrapy.http import Request
import re


class HeBeiprovinceSpider(scrapy.Spider):
    name = 'HeBeiProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.number = 5
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://zfcxjst.hebei.gov.cn/was5/web/search?channelid=247697'
        self.flag = True
        self.data = {'licenseNum': '', 'contactMan': '', 'area': '', 'companyArea': '河北省', 'contactAddress': '',
                     'contactPhone': '', 'token': self.token}

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        page = Selector(response=response).xpath('//a[@class="last-page"]/@href').extract_first()
        cc = 'search\?page=(\d+)\&channelid=(\d+)\&perpage=(\d+)\&outlinepage=(\d+)\&zsbh=\&qymc=\&zzlx='
        info_page = re.findall(cc, page)
        last_page = 'http://zfcxjst.hebei.gov.cn/was5/web/search?page=%s&channelid=2' \
                    '47697&perpage=15&outlinepage=10&zsbh=&qymc=&zzlx=' % (
                        info_page[0][0])
        yield scrapy.Request(
            url=last_page,
            callback=self.parse,
            meta={'page': info_page[0][0]}
        )

    def parse(self, response):
        # print(response.text)
        div_under_table = Selector(response).xpath('//div[@class="tabbox"]/table/tr/td[3]/text()')
        del div_under_table[0]
        print(len(div_under_table))
        for d in div_under_table:
            company_name = d.extract()
            repeat = self.r.sadd('Company_name', company_name)
            if repeat:
                self.data['companyName'] = company_name
                print(self.data, '发送全部数据')
                yield Request(
                    url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                    # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                    method="POST",
                    headers={'Content-Type': 'application/json'},
                    body=json.dumps(self.data),
                    callback=self.zz,
                    meta={'company_name': company_name, 'data': self.data}
                )
            else:
                print('此公司信息已经存在', company_name)
        print(response.meta['page'], type(response.meta['page']))
        page = int(response.meta['page'])
        page -= 1
        if page != 0:
            url = 'http://zfcxjst.hebei.gov.cn/was5/web/search?page=%s&channelid=247697&perpage=15&outlinepage=10' % str(
                page)
            yield scrapy.Request(url=url, callback=self.parse, meta={'page': page})

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
