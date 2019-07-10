import scrapy
from scrapy import Selector
from scrapy.http import Request,Response
import requests
import json


class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    """其实数据"""
    name = 'company_not_action'
    # 其实地址

    def start_requests(self):
        # 起始url
        self.big_url = 'http://jzsc.mohurd.gov.cn'
        # form表单url
        self.url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
        # koken
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        # 本公司接口
        self.tongnie = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompanyBadCredit.htm'
        # 查询公司名称
        self.corporate_name = '安徽省建科建设监理有限公司'
        # 访问并携带参数
        return [scrapy.FormRequest(self.url,
                                   formdata={'qy_name': self.corporate_name},
                                   callback=self.parse)]

    # 公司选择
    def parse(self, response):
        # 进入当前公司
        """选择公司"""
        corporate_url = Selector(response=response).xpath('//td[@class="text-left primary"]/a/@href').extract_first()
        url = self.big_url + corporate_url
        return Request(url=url, callback=self.detailed_information)

    # 企业基本内容---
    def detailed_information(self, response):
        """发送公司基本信息"""
        # yield Request(url=self.tongnie, method="POST", body=json.dumps(self.company_zz), headers={'Content-Type': 'application/json'},callback=self.zz)
        another_url = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li[4]/a/@data-url').extract_first()
        self.action = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li[4]/a/span/text()').extract_first()
        print(self.action)
        another_url = self.big_url +another_url
        print(another_url, '去访问的地址')
        yield Request(url=another_url, callback=self.bad_recode)

    # 不良行为
    def bad_recode(self,response):
        """不良行为"""
        content = Selector(response=response).xpath('//tbody/tr')
        if not content.xpath('./td/text()').extract_first() == "暂未查询到已登记入库信息":
            print(content.xpath('./td/text()').extract_first(), '不良行为相关信息')
            for c in content:
                td = c.xpath('./td')
                not_good = {}
                for t in td:
                    h = t.xpath('@data-header').extract_first()
                    h = h.split()[0]
                    if h == "诚信记录编号":
                        d = t.xpath('./span/text()').extract_first()
                        print("诚信记录编号", d)
                        d = d.split()[0]
                        not_good['creditNum'] = d
                    elif h == "诚信记录主体":
                        d = t.xpath('./a/text()').extract_first()
                        print("诚信记录主体", d)
                        d = d.split()[0]
                        not_good['companyName'] = d
                    elif h == "决定内容":
                        d = t.xpath('./div/span[2]/text()').extract_first()
                        d = d.split('：')[1]
                        print("决定内容", d)
                        not_good['beginDate'] = d
                        content = t.xpath('./div/a/@data-text').extract_first()
                        content = content.split()[0]
                        print("决定内容", content)
                        not_good['fileContent'] = content
                        result = t.xpath('text()')[1].extract()
                        result = result.split()[0]
                        not_good['mark'] = result
                        print("决定内容", result)
                    elif h == "实施部门（文号）":
                        address = t.xpath('text()').extract_first()
                        address = address.split()[0]
                        print('实施部门（文号）', address)
                        not_good['departName'] = address
                        number = t.xpath('./div/text()').extract_first()
                        number = number.split()[0]
                        print('实施部门（文号）', number)
                        not_good['fileNum'] = number
                    elif h == "发布有效期":
                        t = t.xpath('text()').extract_first()
                        t = t.split()[0]
                        not_good['endDate'] = t
                        print('发布有效期', t)
                    not_good['token'] = self.token
                yield Request(url=self.tongnie, method="POST", body=json.dumps(not_good), headers={'Content-Type': 'application/json'}, callback=self.zz)
                print('发送成功----', not_good)
        else:
            print(self.corporate_name, '--没有--', self.action, '这个相关的记录')

    def zz(self, response):
        """企业发送信息回应"""
        print(response.body)