import scrapy
from scrapy import Selector
from scrapy.http import Request,Response
import requests
import json
from scrapy import log


# scrapy.log.start


class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    """其实数据"""
    name = 'company_change_code'

    # 其实地址
    def start_requests(self):
        # 起始url
        self.big_url = 'http://jzsc.mohurd.gov.cn'
        # form表单url
        self.url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
        # token
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        # 本公司接口
        self.tongnie = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompany.htm'
        # 提交form数据
        self.corporate_name = '朝阳市顺达水利工程设计有限公司'
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
        return Request(url=url,callback=self.detailed_information)

    # 企业基本内容---
    def detailed_information(self, response):
        """发送公司基本信息"""
        another_url = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li[8]/a/@data-url').extract_first()
        self.action = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li[8]/a/span/text()').extract_first()
        print(self.action)
        another_url = self.big_url +another_url
        yield Request(url=another_url, callback=self.change_code)

    # 变更记录
    def change_code(self, response):
        content = Selector(response=response).xpath('//tbody/tr')
        if not content.xpath('./td/text()').extract_first() == "暂未查询到已登记入库信息":
            print(content)
            for c in content:
                td = c.xpath('./th')
                not_good = {}
                for t in td:
                    h = t.xpath('@data-url').extract_first()
                    d = t.xpath('text()').extract_first()
                    h = h.split()[0]
                    d = d.split()[0]
                    if h == "序号":
                        not_good['sincerity'] = d
                    elif h == "变更日期":
                        not_good['sincerity_recode'] = d
                    elif h == "变更内容":
                        not_good['sincerity_recode'] = d
        else:
            print(self.corporate_name, '--没有--', self.action, '这个相关的记录')
            # yield Request()

    def zz(self, response):
        """企业发送信息回应"""
        print(response.body)