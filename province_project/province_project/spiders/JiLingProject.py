# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import time
import json
import re
from lxml import etree
from province_project import templates
from province_project import templates


class JiLinProvince(scrapy.Spider):
    name = 'JiLinProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        now_time = time.time() * 1000
        now_time = int(now_time)
        reduce_time = now_time - 1000000
        self.url = 'http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SnCorpData&CorpName=&QualiType=&TradeID=&BoundID=&LevelID=&CityNum=&nPageIndex=%s&nPageCount=0&nPageRowsCount=0&nPageSize=%s&_=%s' % (
            1, 20, reduce_time)
        self.bigurl = 'http://cx.jlsjsxxw.com/'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.number = 5
        self.r = redis.Redis(connection_pool=pool)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        page = json.loads(response.text)['nPageCount']
        print(page, type(page))
        yield scrapy.Request(
            url='http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SnCorpData'
                '&CorpName=&QualiType=&TradeID=&BoundID=&LevelID'
                '=&CityNum=&nPageIndex=%s&nPageCount=0&nPageR'
                'owsCount=0&nPageSize=%s&' % (int(page), 20),
            callback=self.parse,
            meta={'page': int(page)}
        )

    def parse(self, response):
        zz = Selector(response=response).xpath('//tr/td[2]/a/@href')
        for z in zz:
            company_name = z.extract()
            company_name = company_name.split(r'\"')[1]
            url = company_name.split('..')[1]
            xx = '/CorpInfo/.*\.aspx\?rowGuid=.*\&corpid=(.*)\&VType=.*'
            cc = re.findall(xx, url)[0]
            yield scrapy.Request(url=self.bigurl + url, callback=self.company_information, dont_filter=True,
                                 meta={'cc': cc}
                                 )
        page = int(response.meta['page'])
        page -= 1
        if page != 0:
            yield scrapy.Request(url='http://cx.jlsjsxxw.com/handle/NewHandler.ashx?method=SnCorpData'
                                     '&CorpName=&QualiType=&TradeID=&BoundID=&LevelID'
                                     '=&CityNum=&nPageIndex=%s&nPageCount=0&nPageR'
                                     'owsCount=0&nPageSize=%s&' % (page, 20),
                                 callback=self.parse, dont_filter=True,
                                 meta={'page': page}
                                 )

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@class="name_level3"]/text()').extract_first()
        company_name = company_name.split()[0]
        basic_url = 'http://cx.jlsjsxxw.com/handle/Corp_Project.ashx?corpid=%s&_=1556177544518' % response.meta['cc']

        yield scrapy.Request(url=basic_url, callback=self.project, dont_filter=True,
                             meta={'companyName': company_name}
                             )

        # bid_url = 'http://cx.jlsjsxxw.com/handle/ProjectHandler.ashx?method=ztb&PRJID=%s&_=1558339753679' % response.meta['cc']
        # yield scrapy.Request(url=bid_url, callback=self.project_bid, dont_filter=True,
        #                      meta={'companyName': company_name}
        #                      )
        # print(company_name, number, response.meta['cc'])

    def project(self, response):
        tr = templates.jilin_json_url_analysis(response, 2, 'http://cx.jlsjsxxw.com')
        for every_tr in tr:
            yield scrapy.Request(url=every_tr, callback=self.project_basic,
                                 meta={'companyName': response.meta['companyName']})

    def project_basic(self, response):
        name = Selector(response=response).xpath('//td[@colspan="3"]/text()').extract_first()

        code = Selector(response=response).xpath('//td[@class="name_level3 col_01_value"]/text()').extract_first()

        provinceCode = Selector(response=response).xpath('//td[@class="col_02_value"]')[0].xpath(
            'text()').extract_first()

        unit = Selector(response=response).xpath('//td[@class="col_01_value"]')[1].xpath('text()').extract_first()

        catalog = Selector(response=response).xpath('//td[@class="col_02_value"]')[1].xpath('text()').extract_first()

        unitLicenseNum = Selector(response=response).xpath('//td[@class="col_01_value"]')[2].xpath(
            'text()').extract_first()

        area = Selector(response=response).xpath('//td[@class="col_01_value"]')[3].xpath('text()').extract_first()

        docuCode = Selector(response=response).xpath('//td[@class="col_01_value"]')[4].xpath('text()').extract_first()

        level = Selector(response=response).xpath('//td[@class="col_02_value"]')[4].xpath('text()').extract_first()

        money = Selector(response=response).xpath('//td[@class="col_01_value"]')[5].xpath('text()').extract_first()

        acreage = Selector(response=response).xpath('//td[@class="col_02_value"]')[5].xpath('text()').extract_first()

        trait = Selector(response=response).xpath('//td[@class="col_01_value"]')[6].xpath('text()').extract_first()

        purpose = Selector(response=response).xpath('//td[@class="col_02_value"]')[6].xpath('text()').extract_first()

        basic = templates.Project(name=name, companyName=response.meta['companyName'], code=code,
                                  provinceCode=provinceCode, unit=unit, catalog=catalog,
                                  unitLicenseNum=unitLicenseNum, area=area, docuCode=docuCode,
                                  level=level, money=money, acreage=acreage, trait=trait,
                                  purpose=purpose
                                  )
        basic_data = basic.data()
        print(basic_data, '基本信息')
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                             body=json.dumps(basic_data), callback=self.project_zz,
                             headers={'Content-Type': 'application/json'},
                             method='POST',
                             meta={'type': '基本信息',
                                   'company_name': basic_data['companyName']
                                   },

                             )

        xx = 'PrjId=(.*)'

        bid_url = 'http://cx.jlsjsxxw.com/handle/ProjectHandler.ashx?method=ztb&PRJID=%s&_=1556177544518'\
                  % re.findall(xx, response.url)[0]
        yield scrapy.Request(url=bid_url, callback=self.project_bid_list,
                             meta={'companyName': response.meta['companyName'], 'code': code})

        drawing_url = 'http://cx.jlsjsxxw.com/handle/ProjectHandler.ashx?method=sgtsc&PRJID=%s&_=1558342067012' % \
                      re.findall(xx, response.url)[0]
        yield scrapy.Request(url=drawing_url, callback=self.project_drawing_list,
                             meta={'companyName': response.meta['companyName'], 'code': code})

        contract_url = 'http://cx.jlsjsxxw.com/handle/ProjectHandler.ashx?method=htba&PRJID=%s&_=1558342067013' % \
                       re.findall(xx, response.url)[0]
        yield scrapy.Request(url=contract_url, callback=self.project_contract_list,
                             meta={'companyName': response.meta['companyName'], 'code': code})

        construction_url = 'http://cx.jlsjsxxw.com/handle/ProjectHandler.ashx?method=sgxk&PRJID=%s&_=1558342067014' % \
                           re.findall(xx, response.url)[0]
        yield scrapy.Request(url=construction_url, callback=self.project_construction_list,
                             meta={'companyName': response.meta['companyName'], 'code': code})

    def project_bid_list(self, response):
        tr = templates.jilin_json_url_analysis(response, 9)
        for every_tr in tr:
            yield scrapy.Request(url=every_tr, callback=self.bid_info,
                                 meta={'companyName': response.meta['companyName'], 'code': response.meta['code']})

    def project_drawing_list(self, response):
        tr = templates.jilin_json_url_analysis(response, 7)
        for every_tr in tr:
            yield scrapy.Request(url=every_tr, callback=self.drawing_info,
                                 meta={'companyName': response.meta['companyName'], 'code': response.meta['code']})

    def project_contract_list(self, response):
        tr = templates.jilin_json_url_analysis(response, 6)
        for every_tr in tr:
            yield scrapy.Request(url=every_tr, callback=self.contract_info,
                                 meta={'companyName': response.meta['companyName'], 'code': response.meta['code']})

    def project_construction_list(self, response):
        tr = templates.jilin_json_url_analysis(response, 6)
        for every_tr in tr:
            yield scrapy.Request(url=every_tr, callback=self.construction_info,
                                 meta={'companyName': response.meta['companyName'], 'code': response.meta['code']})

    # def project_completed_list(self, response):
    #     tr = templates.jilin_json_url_analysis(response, 7)
    #     print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    #     for every_tr in tr:
    #         print(every_tr, 'ccccccccccccccccccccccc')
    #         yield scrapy.Request(url=every_tr, callback=self.comppleted_info,
    #                              meta={'companyName': response.meta['companyName'], 'code': response.meta['code']})

    def bid_info(self, response):
        attrs = [{'that': '', 'attr': '//td[@class="name_level3 col_01_value"]/span/text()', 'name': 'code'},
                 {'that': '', 'attr': '//span[@id="lblTenderMoney"]/text()', 'name': 'tenderMoney'},
                 {'that': '', 'attr': '//span[@id="lblArea"]/text()', 'name': 'area'},
                 {'that': '', 'attr': '//span[@id="lblTenderNum"]/text()', 'name': 'tenderNum'},
                 {'that': '', 'attr': '//span[@id="lblTenderNum"]/text()', 'name': 'provinceTenderNum'},
                 {'that': '', 'attr': '//span[@id="lblTenderClassNum"]/text()', 'name': 'tenderClass'},
                 {'that': '', 'attr': '//span[@id="lblTenderTypeNum"]/text()', 'name': 'tenderType'},
                 {'that': '', 'attr': '//span[@id="lblTenderResultDate"]/text()', 'name': 'tenderResultDate'},
                 {'that': '', 'attr': '//span[@id="lblPrjSize"]/text()', 'name': 'prjSize'},
                 {'that': '', 'attr': '//span[@id="lblAgencyCorpName"]/text()', 'name': 'agencyCorpName'},
                 {'that': '', 'attr': '//span[@id="lblAgencyCorpCode"]/text()', 'name': 'agencyCorpCode'},
                 {'that': '', 'attr': '//span[@id="lblTenderCorpName"]/text()', 'name': 'tenderCorpName'},
                 {'that': '', 'attr': '//span[@id="lblTenderCorpCode"]/text()', 'name': 'tenderCorpCode'},
                 {'that': '', 'attr': '//span[@id="lblCreateDate"]/text()', 'name': 'createDate'},
                 {'that': '', 'attr': '//span[@id="lblConstructorName"]/text()', 'name': 'constructorName'},
                 {'that': '', 'attr': '//span[@id="lblConstructorIDCard"]/text()', 'name': 'constructorIDCard'},
                 ]
        bid_object = templates.Projects('Mark')
        bid_data = bid_object.html_analysis(response, attrs)
        bid_data['companyName'] = response.meta['companyName']
        bid_zz = templates.Mark(**bid_data)
        bid_zz = bid_zz.data()
        bid_zz['code'] = response.meta['code']
        print(bid_zz, '招标信息')
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
                             body=json.dumps(bid_zz), callback=self.project_zz,
                             headers={'Content-Type': 'application/json'},
                             method='POST',
                             meta={'type': '招标信息'}
                             )

    def drawing_info(self, response):
        attrs = [{'that': '', 'attr': '//span[@id="lblPrjNum"]/text()', 'name': 'code'},
                 {'that': '', 'attr': '//span[@id="lblCensorCorpName"]/text()', 'name': 'censorCorpName'},
                 {'that': '', 'attr': '//span[@id="lblCensorCorpCode"]/text()', 'name': 'censorCorpCode'},
                 {'that': '', 'attr': '//span[@id="lblCensorNum"]/text()', 'name': 'censorNum'},
                 {'that': '', 'attr': '//span[@id="lblCensorNum"]/text()', 'name': 'provinceCensorNum'},
                 {'that': '', 'attr': '//span[@id="lblCensorEDate"]/text()', 'name': 'censorEDate'},
                 {'that': '', 'attr': '//span[@id="lblPrjSize"]/text()', 'name': 'prjSize'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[2]//td[2]/a/text()',
                  'name': 'surveyCorpName'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[2]/td[3]/text()',
                  'name': 'surveyCorpCode'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[2]/td[4]/text()',
                  'name': 'surveyCorpArea'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[3]/td[2]/a/text()',
                  'name': 'designCorpName'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[3]/td[3]/text()',
                  'name': 'designCorpCode'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[3]/td[4]/text()',
                  'name': 'designCorpArea'},
                 ]

        drawing_object = templates.Projects('MakeDrawing')
        drawing_data = drawing_object.html_analysis(response, attrs)
        if drawing_data['censorNum']:
            p_tr = Selector(response=response).xpath('//table[@class="rpd_basic_table"][3]/tr')
            p_tr = p_tr[1:-1]
            engineers = []
            for p in p_tr:
                person = {'companyName': '', 'tradeName': '', 'prjDuty': '', 'name': '', 'card': '',
                          'specialty': ''
                          }
                companyName = p.xpath('./td[1]/text()').extract_first()
                if companyName:
                    person['companyName'] = companyName

                tradeName = p.xpath('./td[2]/text()').extract_first()
                if tradeName:
                    person['tradeName'] = tradeName

                prjDuty = p.xpath('./td[3]/text()').extract_first()
                if prjDuty:
                    person['prjDuty'] = prjDuty

                name = p.xpath('./td[4]/text()').extract_first()
                if name:
                    person['name'] = name

                card = p.xpath('./td[5]/text()').extract_first()
                if card:
                    person['card'] = card

                specialty = p.xpath('./td[6]/text()').extract_first()
                if specialty:
                    person['specialty'] = specialty

                if person['name']:
                    engineers.append(person)
            drawing_data['engineers'] = engineers
            drawing_data['companyName'] = response.meta['companyName']
            drawing_zz = templates.MakeDrawing(**drawing_data)
            print(drawing_zz.data(), '施工图纸审查')
            drawing_xx = drawing_zz.data()
            drawing_xx['code'] = response.meta['code']
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectCensor.htm',
                                 body=json.dumps(drawing_xx), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '施工图纸审查'}
                                 )

    def contract_info(self, response):
        attrs = [{'that': '', 'attr': '//span[@id="lblPrjNum"]/text()', 'name': 'code'},
                 {'that': '', 'attr': '//span[@id="lblRecordNum"]/text()', 'name': 'recordNum'},
                 {'that': '', 'attr': '//span[@id="lblRecordNum"]/text()', 'name': 'provinceRecordNum'},
                 {'that': '', 'attr': '//span[@id="lblContractNum"]/text()', 'name': 'contractNum'},
                 {'that': '', 'attr': '//span[@id="lblcontractclassnum"]/text()', 'name': 'contractClassify'},
                 {'that': '', 'attr': '//span[@id="lblContractTypeNum"]/text()', 'name': 'contractType'},
                 {'that': '', 'attr': '//span[@id="lblContractMoney"]/text()', 'name': 'contractMoney'},
                 {'that': '', 'attr': '//span[@id="lblPrjSize"]/text()', 'name': 'prjSize'},
                 {'that': '', 'attr': '//span[@id="lblContractDate"]/text()', 'name': 'contractDate'},
                 {'that': '', 'attr': '//span[@id="lblPropietorCorpName"]/text()', 'name': 'proprietorCorpName'},
                 {'that': '', 'attr': '//span[@id="lblPropietorCorpCode"]/text()', 'name': 'proprietorCorpCode'},
                 {'that': '', 'attr': '//span[@id="lblContractorCorpName"]/text()', 'name': 'contractorCorpName'},
                 {'that': '', 'attr': '//span[@id="lblContractorCorpCode"]/text()', 'name': 'contractorCorpCode'},
                 {'that': '', 'attr': '//span[@id="lblUnionCorpName"]/text()', 'name': 'unionCorpName'},
                 {'that': '', 'attr': '//span[@id="lblUnionCorpCode"]/text()', 'name': 'unionCorpCode'},
                 {'that': '', 'attr': '//span[@id="lblCreateDate"]/text()', 'name': 'createDate'},
                 ]
        contract_object = templates.Projects('Contract')
        contract_data = contract_object.html_analysis(response, attrs)
        contract_data['companyName'] = response.meta['companyName']
        contract_zz = templates.Contract(**contract_data)
        contract_zz = contract_zz.data()
        print(contract_zz, '合同备案信息')
        contract_zz['code'] = response.meta['code']
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectContract.htm',
                             body=json.dumps(contract_zz), callback=self.project_zz,
                             headers={'Content-Type': 'application/json'}, method='POST',
                             meta={'type': '合同备案信息'}
                             )

    def construction_info(self, response):
        attrs = [{'that': '', 'attr': '//span[@id="lblPrjNum"]/text()', 'name': 'code'},
                 {'that': '', 'attr': '//span[@id="lblBuilderLicenceNum"]/text()', 'name': 'builderLicenceNum'},
                 {'that': '', 'attr': '//span[@id="lblBuilderLicenceNum"]/text()', 'name': 'provinceBuilderLicenceNum'},
                 {'that': '', 'attr': '//span[@id="lblCensorNum"]/text()', 'name': 'censorNum'},
                 {'that': '', 'attr': '//span[@id="lblContractMoney"]/text()', 'name': 'contractMoney'},
                 {'that': '', 'attr': '//span[@id="lblArea"]/text()', 'name': 'area'},
                 {'that': '', 'attr': '//span[@id="lblConstructorName"]/text()', 'name': 'constructorName'},
                 {'that': '', 'attr': '//span[@id="lblConstructorIDCard"]/text()', 'name': 'constructorIDCard'},
                 {'that': '', 'attr': '//span[@id="lblSupervisionName"]/text()', 'name': 'supervisionName'},
                 {'that': '', 'attr': '//span[@id="lblSupervisionIDCard"]/text()', 'name': 'supervisionIDCard'},
                 {'that': '', 'attr': '//span[@id="lblCreateDate"]/text()', 'name': 'createDate'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[2]/td[2]/a/text()',
                  'name': 'designCorpName'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[2]/td[3]/text()',
                  'name': 'designCorpCode'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[2]/td[4]/text()',
                  'name': 'designCorpArea'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[3]/td[2]/a/text()',
                  'name': 'consCorpName'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[3]/td[3]/text()',
                  'name': 'consCorpCode'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[3]/td[4]/text()',
                  'name': 'consCorpArea'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[4]/td[2]/a/text()',
                  'name': 'superCorpName'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[4]/td[3]/text()',
                  'name': 'superCorpCode'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[4]/td[4]/text()',
                  'name': 'superCorpArea'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[5]/td[2]/a/text()',
                  'name': 'econCorpName'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[5]/td[3]/text()',
                  'name': 'econCorpCode'},
                 {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[5]/td[4]/text()',
                  'name': 'econCorpArea'},
                 ]
        contract_object = templates.Projects('ConstructionPermit')
        construction_data = contract_object.html_analysis(response, attrs)
        construction_data['companyName'] = response.meta['companyName']
        construction_zz = templates.ConstructionPermit(**construction_data)
        construction_zz = construction_zz.data()
        print(construction_zz, '施工许可信息')
        construction_zz['code'] = response.meta['code']
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectBuilderLicence.htm',
                             body=json.dumps(construction_zz), callback=self.project_zz,
                             headers={'Content-Type': 'application/json'}, method='POST',
                             meta={'type': '施工许可信息'}
                             )

    # def comppleted_info(self, response):
    #     attrs = [{'that': '', 'attr': '//span[@id="lblPrjNum"]/text()', 'name': 'code'},
    #              {'that': '', 'attr': '//span[@id="lblBuilderLicenceNum"]/text()', 'name': 'builderLicenceNum'},
    #              {'that': '', 'attr': '//span[@id="lblBuilderLicenceNum"]/text()', 'name': 'provinceBuilderLicenceNum'},
    #              {'that': '', 'attr': '//span[@id="lblCensorNum"]/text()', 'name': 'censorNum'},
    #              {'that': '', 'attr': '//span[@id="lblContractMoney"]/text()', 'name': 'contractMoney'},
    #              {'that': '', 'attr': '//span[@id="lblArea"]/text()', 'name': 'area'},
    #              {'that': '', 'attr': '//span[@id="lblConstructorName"]/text()', 'name': 'constructorName'},
    #              {'that': '', 'attr': '//span[@id="lblConstructorIDCard"]/text()', 'name': 'constructorIDCard'},
    #              {'that': '', 'attr': '//span[@id="lblSupervisionName"]/text()', 'name': 'supervisionName'},
    #              {'that': '', 'attr': '//span[@id="lblSupervisionIDCard"]/text()', 'name': 'supervisionIDCard'},
    #              {'that': '', 'attr': '//span[@id="lblCreateDate"]/text()', 'name': 'createDate'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[2]/td[2]/a/text()',
    #               'name': 'designCorpName'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[2]/td[3]/text()',
    #               'name': 'designCorpCode'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[2]/td[4]/text()',
    #               'name': 'designCorpArea'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[3]/td[2]/a/text()',
    #               'name': 'consCorpName'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[3]/td[3]/text()',
    #               'name': 'consCorpCode'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[3]/td[4]/text()',
    #               'name': 'consCorpArea'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[4]/td[2]/a/text()',
    #               'name': 'superCorpName'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[4]/td[3]/text()',
    #               'name': 'superCorpCode'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[4]/td[4]/text()',
    #               'name': 'superCorpArea'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[5]/td[2]/a/text()',
    #               'name': 'econCorpName'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[5]/td[3]/text()',
    #               'name': 'econCorpCode'},
    #              {'that': '', 'attr': '//table[@class="rpd_basic_table"][2]/tr[5]/td[4]/text()',
    #               'name': 'econCorpArea'},
    #              ]
    #     contract_object = templates.Projects('ConstructionPermit')
    #     construction_data = contract_object.html_analysis(response, attrs)
    #     construction_data['companyName'] = response.meta['companyName']
    #     print(construction_data, response.meta['companyName'], response.meta['name'])
    #     construction_zz = templates.ConstructionPermit(**construction_data)
    #     construction_zz = construction_zz.data()
    #     print(construction_zz)
    #     yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
    #                          body=json.dumps(construction_zz), callback=self.project_zz,
    #                              headers={'Content-Type': 'application/json'}, method='POST'
    #                          )

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

    def project_zz(self, response):
        not_company_code = json.loads(response.text)['code']
        if not_company_code == -102 and response.meta['type'] == '基本信息':
            not_search_company_name = response.meta['company_name']
            self.r.sadd('title_name1', not_search_company_name)
            print('正在添加公司基本信息', not_search_company_name)
        else:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>%s------%s' % (response.text, response.meta['type'],))
