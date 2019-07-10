import scrapy
from scrapy import Selector
from scrapy.http import Request,Response
import requests
import json

class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    """其实数据"""
    name = 'company_good_action'
    # 其实地址
    def start_requests(self):
        # 起始url
        self.big_url = 'http://jzsc.mohurd.gov.cn'
        # form表单url
        self.url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
        # token
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        # 公司接口
        # self.tongnie = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompany.htm'
        self.tongnie = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompanyGoodCredit.htm'
        # 传递参数
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
        # yield Request(url=self.tongnie, method="POST", body=json.dumps(self.company_zz), headers={'Content-Type': 'application/json'},callback=self.zz)
        another_url = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li[5]/a/@data-url').extract_first()
        self.action = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li[5]/a/span/text()').extract_first()
        print(self.action)
        another_url = self.big_url + another_url
        yield Request(url=another_url, callback=self.good_recode)
    # 良好行为
    def good_recode(self,response):
        """良好行为"""
        content = Selector(response=response).xpath('//tbody/tr')
        # if not content.xpath('./td/text()').extract_first() == "暂未查询到已登记入库信息":
        #     f = open('corporate_name.txt', 'a+', encoding='utf-8')
        #     print('公司良好行为有------次公司为', self.corporate_name, '请注意')
        #     f.write(self.corporate_name + '此公司拥有良好行为' + '\n')
        #     f.close()
        #     for c in content:
        #         td = c.xpath('./th')
        #         not_good = {}
        #         good = {}
        #         for t in td:
        #             h = t.xpath('@data-url').extract_first()
        #             d = t.xpath('text()').extract_first()
        #             h = h.split()[0]
        #             d = d.split()[0]
        #             if h == "诚信记录编号":
        #                 not_good['sincerity'] = d
        #             elif h == "诚信记录主体":
        #                 not_good['sincerity_recode'] = d
        #             elif h == "决定内容":
        #                 not_good['department'] = d
        #             elif h == "实施部门（文号）":
        #                 not_good['implementation_department'] = d
        #             elif h == "发布有效期":
        #                 not_good['data'] = d
        #         good['creditNum'] = ''
        #         good['companyName'] = ''
        #         good['beginDate'] = ''
        #         good['fileContent'] = ''
        #         good['mark'] = ''
        #         good['departName'] = ''
        #         good['fileNum'] = ''
        #         good['endDate'] = ''
        #         good['token'] = self.token
        #         yield Request(url=self.tongnie, method="POST", body=json.dumps(good), headers={'Content-Type': 'application/json'}, callback=self.zz)
        # else:
        #     print(self.corporate_name, '--没有--', self.action, '这个相关的记录')
            # yield Request()
        good = {}
        good['creditNum'] = ''
        good['companyName'] = ''
        good['beginDate'] = ''
        good['fileContent'] = ''
        good['mark'] = ''
        good['departName'] = ''
        good['fileNum'] = ''
        good['endDate'] = ''
        good['token'] = self.token
        print(good)
        yield Request(url=self.tongnie, method="POST", body=json.dumps(good),
                      headers={'Content-Type': 'application/json'}, callback=self.zz)
    def zz(self,response):
        """企业发送信息回应"""
        print(response.text)