# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re


class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'new_hubei'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {'companyArea': '湖北省', 'area': '', 'contactAddress': '', 'contactMan': '', 'contactPhone': '',
                     'token': self.token}
        self.url = [{'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=1': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=2': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=3': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=4': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=5': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=6': 1},
                    {'http://59.175.169.110/web/QyManage/QyList.aspx?qylx=7': 1},
                    ]
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.index = 1
        self.G = None
        self.b_page = True

    def start_requests(self):
        for i in self.url:
            for v, k in i.items():
                yield scrapy.Request(url=v, callback=self.parse, dont_filter=True, meta={'page': k})

    def parse(self, response):
        psot_forma_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        psot_forma_data['__VIEWSTATE'] = __VIEWSTATE
        psot_forma_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        psot_forma_data['__EVENTTARGET'] = 'lbtnNext'
        now_url = response.url
        now_number = 'http://59.175.169.110/web/QyManage/QyList.aspx\?qylx=(\d)'
        zz = re.findall(now_number, now_url)[0]
        psot_forma_data['hfQylx'] = zz
        page = Selector(response=response).xpath('//span[@id="labPageCount"]/text()').extract_first()
        now_page = int(page)
        now_page += 1
        whole_company_information = Selector(response=response).xpath('//table[@class="table"]/tr')
        print('当前一页的长度%s' % len(whole_company_information))
        for c_info in whole_company_information:
            company_name = c_info.xpath('./td[2]/a/text()').extract_first()
            number = c_info.xpath('./td[3]/text()').extract_first()
            if company_name is None or company_name == []:
                continue
            company_name = company_name.split()[0]
            if number is not None and number.split() != []:
                number = number.split()[0]
                # print(number)
                if len(number) == 18:
                    self.data['licenseNum'] = number
                else:
                    self.data['licenseNum'] = ''
            else:
                self.data['licenseNum'] = ''
            self.data['companyName'] = company_name
            print(self.data)
            yield scrapy.Request(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                method="POST",
                headers={'Content-Type': 'application/json'},
                body=json.dumps(self.data),
                callback=self.zz,
                meta={'company_name': company_name, 'data': self.data},
                dont_filter=True
            )
        now_page = int(page)
        now_page += 1
        index = int(response.meta['page']) + 1
        if index != now_page:
            psot_forma_data['txtPageIndex'] = str(index)
            print('这个网页的地址是%s----这是它的第%s页-----她总共%s页' % (response.url, index, now_page))
            yield scrapy.FormRequest(url=response.url,
                                     formdata=psot_forma_data,
                                     callback=self.parse,
                                     meta={'page': index},
                                     dont_filter=True)

    def zz(self, response):
        not_company_code = json.loads(response.text)['code']
        not_search_company_name = response.meta['company_name']
        zz_data = response.meta['data']
        self.r.sadd('all_company_name', not_search_company_name)
        print(response.text)
        data = json.dumps(zz_data, ensure_ascii=False)
        print('接口发送的数据%s' % data)
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')

    # def company_information(self,response):
    #     company_name = Selector(response=response).xpath('//td[@id="QYMC"]/text()').extract_first()
    #     print(company_name)
