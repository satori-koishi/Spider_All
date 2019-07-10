import scrapy
from scrapy import Selector
from scrapy.http import Request,Response
import requests
import json
import redis


class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    """其实数据"""
    name = 'company_not_respect'

    # 其实地址
    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.big_url = 'http://jzsc.mohurd.gov.cn'
        # 起始url
        # form表单url
        self.url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
        # token
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        # 本公司接口
        # self.tongnie = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompanyUnCredit.htm'
        self.tongnie = 'https://api.maotouin.com/rest/companyInfo/addCompanyUnCredit.htm'
        # 提交form数据
        self.corporate_name = '农安县龙华建筑工程有限公司'
        # 链接redis
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)

    def start_requests(self):
        have_company = self.r.scard('company_respect')
        action = True
        if have_company is 0:
            action = False
        while action:
            company_name = self.r.spop('company_respect')

            return [scrapy.FormRequest(self.url,
                                       formdata={'qy_name': company_name},
                                       callback=self.parse,
                                       meta={'company_name': company_name}
                                       )
                    ]

    # 公司选择
    def parse(self, response):
        # 进入当前公司
        """选择公司"""
        corporate_url = Selector(response=response).xpath('//td[@class="text-left primary"]/a/@href').extract_first()
        if corporate_url is not None:
            url = self.big_url + corporate_url
            return Request(url=url, callback=self.detailed_information,
                           meta={'company_name': response.meta['company_name']})
        print('对不起没找到当前公司')
        self.r.sadd(response.meta['company_name'], 'company_not_respect')

    # 企业基本内容---
    def detailed_information(self, response):
        """发送公司基本信息"""
        another_url = Selector(response=response).\
            xpath('//ul[@class="tinyTab datas_tabs"]/li[7]/a/@data-url').extract_first()
        another_url = self.big_url + another_url
        return Request(url=another_url, callback=self.record_dishonesty,
                       meta={'company_name': response.meta['company_name']})

    # 失信联合惩戒记录
    def record_dishonesty(self, response):
        """失信联合惩戒记录"""
        print('失信联合惩戒记录------- ')
        content = Selector(response=response).xpath('//tbody/tr')
        if not content.xpath('./td/text()').extract_first() == "暂未查询到已登记入库信息":
            print(content)
            for c in content:
                td = c.xpath('./td')
                not_good = {}
                for t in td:
                    # print(t)
                    h = t.xpath('@data-header').extract_first()
                    h = h.split()[0]
                    if h == "失信联合惩戒记录编号":
                        d = t.xpath('./span/text()').extract_first()
                        d = d.split()[0]
                        not_good['unCreditNum'] = d
                    elif h == "失信联合惩戒记录主体":
                        d = t.xpath('./a/text()').extract_first()
                        d = d.split()[0]
                        not_good['companyName'] = d
                    elif h == "法人姓名":
                        d = t.xpath('./div/span/text()').extract_first()
                        d2 = t.xpath('text()')[1].extract()
                        d = d.split()[0]
                        d2 = d2.split()[0]
                        not_good['legalMan'] = d
                        not_good['legalManIDCard'] = d2
                    elif h == "列入名单事由":
                        div = t.xpath('text()')[1].extract()
                        div = div.split()[0]
                        a = t.xpath('./div/a/@data-text').extract_first()
                        a = a.split()[0]
                        span = t.xpath('./div/span/text()').extract_first()
                        span = span.split('：')[1]
                        d = div + a + span
                        not_good['reason'] = div
                        not_good['fileContent'] = a
                        not_good['fileNum'] = span
                    elif h == "认定部门":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        not_good['departName'] = d
                    elif h == "列入日期":
                        d = t.xpath('text()').extract_first()
                        not_good['beginDate'] = d
                not_good['token'] = self.token
                print(not_good, '发送的数据')
                yield Request(url=self.tongnie, method="POST", body=json.dumps(not_good),
                              headers={'Content-Type': 'application/json'}, callback=self.zz)
        else:
            self.r.sadd(response.meta['company_name'], 'without_search_respect_company')
            print('--没有--', response.meta['company_name'], '这个相关的记录')
                # yield Request()

    # 服务器收到后回复
    def zz(self, response):
        """企业发送信息回应"""
        print(response.text)