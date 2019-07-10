import scrapy
from scrapy import Selector
from scrapy.http import Request,Response
import requests
import json
class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    name = 'text'
    # start_requests = 'http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffDetail/001812010345982636'
    start_urls = ['http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffDetail/001812010345982636']
    # def start_requests(self):
    #     """爬虫起始"""
    #     self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
    #     # 本公司接口
    #     self.tongnie = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompanyEngineer.htm'
    #     # 起始url
    #     self.big_url = 'http://jzsc.mohurd.gov.cn'
    #     # form表单url
    #     self.url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
    #     # 提交form数据
    #     self.corporate_name = '浙江大成工程项目管理有限公司'
    #     # 访问并携带参数
    #     return [scrapy.FormRequest(self.url,
    #                                formdata={'qy_name': self.corporate_name},
    #                                callback=self.parse)]

    def parse(self, response):
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        self.tongnie = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompanyEngineer.htm'
        dd = Selector(response=response).xpath('//div[@class="tinyTabContent query_info_dl datas_tabs_box"]/div[@class="activeTinyTabContent"]/dl/dd')
        person_document = {}
        for d in dd:
            one_person_data = d.xpath('./span/text()').extract_first()
            print(one_person_data)
            # if len(dd) == 5:
            #     person_document['major'] = ''
            if one_person_data == '注册类别：':
                register_type = d.xpath('./b/text()').extract_first()
                if register_type ==  None:
                    person_document['grade'] = ''
                person_document['grade'] = register_type

            elif one_person_data == '注册专业：':
                register_major = d.xpath('text()').extract_first()
                if register_major ==  None:
                    person_document['major'] = ''
                else:
                    # person_document['major'] = register_major
                    person_document['major'] = ''

            elif one_person_data == '证书编号：':
                certificate_number = d.xpath('text()').extract_first()
                print('zzzz')
                print(certificate_number)
                if certificate_number == [] or certificate_number == None:
                    print('zzzzz')
                    print(certificate_number)
                    person_document['num'] = ''
                else:
                    print('AAAA')
                    person_document['num'] = certificate_number

            elif one_person_data == '执业印章号：':
                practice_seal_number = d.xpath('text()').extract_first()

                if practice_seal_number == []:
                    person_document['sealNum'] = ''
                person_document['sealNum'] = practice_seal_number
            elif one_person_data == '有效期：':
                term_of_validity = d.xpath('text()').extract_first()
                if term_of_validity == []:
                    person_document['validTime'] = ''
                else:
                    term_of_validity = term_of_validity.replace('年', '-')
                    term_of_validity = term_of_validity.replace('月', '-')
                    term_of_validity = term_of_validity.split('日')[0]
                    person_document['validTime'] = term_of_validity

            elif one_person_data == '注册单位：':
                registered_unit = d.xpath('./a/text()').extract_first()
                if registered_unit == []:
                    person_document['companyName'] = ''
                else:
                    registered_unit = registered_unit.split()[0]
                    person_document['companyName'] = registered_unit
            # 证件信息发送一条
        person_document['token'] = self.token
        person_document['name'] = '钟志林'
        person_document['sex'] = '男'
        person_document['companyName'] = '浙江大成工程项目管理有限公司'
        person_document['card'] = '3622281982******55'
        person_document['idType'] = '其它'

        print(person_document)
        yield Request(url=self.tongnie, method="POST", body=json.dumps(person_document),
                      headers={'Content-Type': 'application/json'}, callback=self.zz)

    def zz(self, response):
        print(response.text)
