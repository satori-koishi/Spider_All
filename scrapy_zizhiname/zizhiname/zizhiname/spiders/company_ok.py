import scrapy
from scrapy import  Selector
from scrapy.http import Request,Response
import json

class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    """其实数据"""
    name = 'company_ok'
    # 其实地址
    def start_requests(self):
        # 起始url
        self.big_url = 'http://jzsc.mohurd.gov.cn'
        # form表单url
        self.url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
        # 提交form数据
        self.corporate_name = '农安县龙华建筑工程有限公司'
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
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        # 本公司接口
        self.tongnie = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompany.htm'
        # 传递参数
        self.company_zz = {}
        # 获取当前公司名称
        self.company_information = Selector(response=response).xpath('//div[@class="user_info spmtop"]/b/text()').extract_first()
        # 获取公司基本信息
        self.company_zz['name'] = self.company_information
        table_information = Selector(response=response).xpath('//table[@class="pro_table_box datas_table"]/tbody/tr')
        for t in table_information:
            # 公司key
            table_hand = t.xpath('./td')
            # if len(table_hand) == 1：
            for a in table_hand:
                # print(a)
                td = a.xpath('./@data-header').extract_first()
                # print(td)
                if not td == None:
                    td = td.split()[0]
                # 公司value
                table_body = a.xpath('./text()').extract_first()
                # print(table_body)
                # 去除空格
                if not table_body == None:
                    table_body = table_body.split()
                    # print(table_hand)
                    if td == '组织机构代码/营业执照编号':
                        # a = table_body[0]
                        b = table_body[2]
                        # userdata = a + '/' + b
                        self.company_zz['corpCode'] = b
                        self.company_zz['licenseNum'] = ''
                    elif td == '统一社会信用代码':
                        self.company_zz['corpCode'] = ''
                        self.company_zz['licenseNum'] = table_body[0]
                    elif td == '企业法定代表人':
                        self.company_zz['legalMan'] = table_body[0]
                    elif td == '企业登记注册类型':
                        self.company_zz['econType'] = table_body[0]
                    elif td == '企业注册属地':
                        self.company_zz['area'] = table_body[0]
                    elif td == '企业经营地址':
                        self.company_zz['address'] = table_body[0]

        self.company_zz['token'] = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        # print(self.company_zz)
        yield Request(url=self.tongnie, method="POST", body=json.dumps(self.company_zz), headers={'Content-Type': 'application/json'},callback=self.zz)
        # another_url = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li')
        # for a in another_url:
        #     a_detailed = a.xpath('./a/span/text()').extract_first()
        #     a_detailed = a_detailed.split()[0]
        #     a_url = a.xpath('./a/@data-url').extract_first()
        #     if a_detailed == '不良行为':
        #         sand_url = self.big_url + a_url
        #         # yield Request(url=sand_url, callback=self.bad_recode)
        #     elif a_detailed == '良好行为':
        #         sand_url = self.big_url + a_url
        #         # yield Request(url=sand_url, callback=self.good_recode)
        #     elif a_detailed == '黑名单记录':
        #         sand_url = self.big_url + a_url
        #         yield Request(url=sand_url, callback=self.blacklist_recode)
        #     elif a_detailed == '失信联合惩戒记录':
        #         sand_url = self.big_url + a_url
        #         # yield Request(url=sand_url, callback=self.record_dishonesty)
        #     elif a_detailed == '变更记录':
        #         sand_url = self.big_url + a_url
        #         # yield Request(url=sand_url, callback=self.change_code)
    # 不良行为
    def bad_recode(self,response):
        """不良行为"""
        content = Selector(response=response).xpath('//tbody/tr')
        if not content.xpath('text()').extract_first() == None:
            print(content)
            for c in content:
                td = c.xpath('./th')
                not_good = {}
                for t in td:
                    h = t.xpath('@data-url').extract_first()
                    d = t.xpath('text()').extract_first()
                    h = h.split()[0]
                    d = d.split()[0]
                    if h == "诚信记录编号":
                        not_good['sincerity'] = d
                    elif h == "诚信记录主体":
                        not_good['sincerity_recode'] = d
                    elif h == "决定内容":
                        not_good['department'] = d
                    elif h == "实施部门（文号）":
                        not_good['implementation_department'] = d
                    elif h == "发布有效期":
                        not_good['data'] = d
            # yield Request()
    # 良好行为
    def good_recode(self,response):
        """良好行为"""
        content = Selector(response=response).xpath('//tbody/tr')
        if not content.xpath('text()').extract_first() == None:
            print(content)
            for c in content:
                td = c.xpath('./th')
                not_good = {}
                for t in td:
                    h = t.xpath('@data-header').extract_first()
                    d = t.xpath('text()').extract_first()
                    h = h.split()[0]
                    d = d.split()[0]
                    if h == "诚信记录编号":
                        not_good['sincerity'] = d
                    elif h == "诚信记录主体":
                        not_good['sincerity_recode'] = d
                    elif h == "决定内容":
                        not_good['department'] = d
                    elif h == "实施部门（文号）":
                        not_good['implementation_department'] = d
                    elif h == "发布有效期":
                        not_good['data'] = d
                # yield Request()
    # 黑名单记录
    def blacklist_recode(self,response):
        content = Selector(response=response).xpath('//tbody/tr')
        if not content.xpath('text()').extract_first() == None:
            print(content, '嘿嘿嘿嘿嘿')
            for c in content:
                td = c.xpath('./td')
                not_good = {}
                for t in td:
                    h = t.xpath('@data-header').extract_first()
                    h = h.split()[0]
                    if h == "黑名单记录编号":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        not_good['sincerity'] = d
                        print('黑名单记录编号',d)
                    elif h == "黑名单记录主体":
                        d = t.xpath('./a/text()').extract_first()
                        d = d.split()[0]
                        not_good['sincerity_recode'] = d
                        print('黑名单记录主体',d)
                    elif h == "黑名单认定依据":
                        d = t.xpath('text()')[1].extract()
                        d = d.split()[0]
                        head = d.split('。')[0]
                        body = d.split('。')[1]
                        d = head+body
                        not_good['department'] = d
                        print('黑名单认定依据', d)
                    elif h == "认定部门":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        not_good['implementation_department'] = d
                        print('认定部门', d)
                    elif h == "列入黑名单日期":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        d = d.replace('年', '-')
                        d = d.replace('月', '-')
                        d = d.replace('日','')
                        not_good['into_data'] = d
                        print('列入黑名单日期',d)
                    elif h == "移出黑名单日期":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        d = d.replace('年', '-')
                        d = d.replace('月', '-')
                        d = d.replace('日', '')
                        not_good['out_data'] = d
                        print('移出黑名单日期', d)
                print(not_good)
                # yield Request()
    # 失信联合惩戒记录
    def record_dishonesty(self,response):
        """失信联合惩戒记录"""
        print('失信联合惩戒记录------- ')
        content = Selector(response=response).xpath('//tbody/tr')
        if not content.xpath('text()').extract_first() == None:
            print(content)
            for c in content:
                td = c.xpath('./td')
                not_good = {}
                for t in td:
                    print(t)
                    h = t.xpath('@data-header').extract_first()
                    h = h.split()[0]
                    if h == "失信联合惩戒记录编号":
                        d = t.xpath('./span/text()').extract_first()
                        d = d.split()[0]
                        not_good['sincerity'] = d
                    elif h == "失信联合惩戒记录主体":
                        d = t.xpath('./a/text()').extract_first()
                        d = d.split()[0]
                        not_good['sincerity_recode'] = d
                    elif h == "法人姓名":
                        d = t.xpath('./div/span/text()').extract_first()
                        d2 = t.xpath('text()')[1].extract()
                        d = d.split()[0]
                        d2 = d2.split()[0]
                        not_good['person_name'] = d
                        not_good['card'] = d2
                    elif h == "列入名单事由":
                        div = t.xpath('text()')[1].extract()
                        div = div.split()[0]
                        a = t.xpath('./div/a/@data-text').extract_first()
                        a = a.split()[0]
                        span = t.xpath('./div/span/text()').extract_first()
                        span = span.split('：')[1]
                        print(span)
                        d = div + a + span
                        not_good['implementation_department'] = d
                    elif h == "认定部门":
                        d = t.xpath('text()').extract_first()
                        d = d.split()[0]
                        not_good['identification '] = d
                    elif h == "列入日期":
                        d = t.xpath('text()').extract_first()
                        not_good['data'] = d
                print(not_good)
                # yield Request()
    # 更改记录
    def change_code(self, response):
        content = Selector(response=response).xpath('//tbody/tr')
        if not content.xpath('text()').extract_first() == None:
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
            # yield Request()
    def zz(self,response):
        """企业发送信息回应"""
        print(response.text)