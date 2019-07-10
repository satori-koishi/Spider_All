import scrapy
from scrapy import Selector
from scrapy.http import Request, Response
import requests
import json
import redis
import re


class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    """其实数据"""
    name = 'company_black_code'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.big_url = 'http://jzsc.mohurd.gov.cn'
        # 起始url
        # form表单url
        self.url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
        # 提交form数据
        self.corporate_name = '福建九宇建设工程有限公司'
        # 访问并携带参数
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        # 本地接口
        # self.tongna = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompanyBlackList.htm'
        # 远程接口
        self.tongna = 'https://api.maotouin.com/rest/companyInfo/addCompanyBlackList.htm'
        # 链接redis
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)

    def start_requests(self):

        have_company = self.r.scard('company_black_code')
        print(have_company)
        while have_company:
            company_name = self.r.spop('company_black_code')
            return [scrapy.FormRequest(self.url,
                                       formdata={'qy_name': company_name},
                                       callback=self.parse,
                                       meta={'company_name': company_name}
                                       )
                        ]
        # except TypeError:
        #     print('zzzzzzzzz')


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
        self.r.sadd(response.meta['company_name'], 'no_search_company_black')

    # 企业基本内容---
    def detailed_information(self, response):
        """发送公司基本信息"""
        another_url = Selector(response=response).xpath(
            '//ul[@class="tinyTab datas_tabs"]/li[6]/a/@data-url').extract_first()
        action = Selector(response=response).xpath(
            '//ul[@class="tinyTab datas_tabs"]/li[6]/a/span/text()').extract_first()
        print(action)
        another_url = self.big_url + another_url
        return Request(url=another_url, callback=self.blacklist_recode,
                       meta={'company_name': response.meta['company_name']})

    # 黑名单
    def blacklist_recode(self, response):
        content = Selector(response=response).xpath('//tbody/tr')
        if not content.xpath('./td/text()').extract_first() == "暂未查询到已登记入库信息":
            for c in content:
                td = c.xpath('./td')
                not_good = {}
                for t in td:
                    h = t.xpath('@data-header').extract_first()
                    h = h.split()[0]
                    if h == "黑名单记录编号":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        not_good['blackListNum'] = d
                        print('黑名单记录编号', d)
                    elif h == "黑名单记录主体":
                        company_name = t.xpath('./a/text()').extract_first()
                        company_name = company_name.split()[0]
                        not_good['companyName'] = company_name
                        print('黑名单记录主体', company_name)
                    elif h == "黑名单认定依据":
                        d = t.xpath('text()')[1].extract()
                        print(d, 'ZZZZZZZZZZZZZZZZZZ')
                        d = d.split()
                        print(d, 'hhhhhhhhhhhhhhhh')
                        if len(d) == 1:
                            head = d[0]
                            bb = '(.*?)（(.*)）'
                            zz = re.findall(bb, head)
                            head = zz[0][0]
                            body = zz[0][1]
                            print(head, 'wwwwwwwwwwwwwwwww')
                        else:
                            head = d[0] + d[1]
                            body = d[1].split('。')[1]
                            body = body.replace('（', '')
                            body = body.replace('）', '')
                        not_good['fileContent'] = head
                        not_good['fileNum'] = body
                        print('黑名单认定依据', d)
                    elif h == "认定部门":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        not_good['departName'] = d
                        print('认定部门', d)
                    elif h == "列入黑名单日期":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        d = d.replace('年', '-')
                        d = d.replace('月', '-')
                        d = d.replace('日', '')
                        not_good['beginDate'] = d
                        print('列入黑名单日期', d)
                    elif h == "移出黑名单日期":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        d = d.replace('年', '-')
                        d = d.replace('月', '-')
                        d = d.replace('日', '')
                        not_good['endDate'] = d
                        print('移出黑名单日期', d)
                # not_good['companyName'] = company_name
                not_good['token'] = self.token
                yield Request(url=self.tongna, method="POST", body=json.dumps(not_good),
                              headers={'Content-Type': 'application/json'}, callback=self.zz)
                print(not_good)
                # yield Request()
        else:
            self.r.sadd(response.meta['company_name'], 'without_search_black_company')
            print('--没有--', response.meta['company_name'], '这个相关的记录')

    def zz(self, response):
        """企业发送信息回应"""
        print(response.text)
