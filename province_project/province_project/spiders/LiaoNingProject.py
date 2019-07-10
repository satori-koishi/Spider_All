# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import re
import json
import time
from province_project import templates


class LiaoNingProvince(scrapy.Spider):
    name = 'LiaoNingProvince'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.url = 'http://218.60.144.163/LNJGPublisher/corpinfo/CorpInfo.aspx'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.number = 5
        self.r = redis.Redis(connection_pool=pool)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer, dont_filter=True)

    def page_transfer(self, response):
        __VIEWSTATE = Selector(response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __EVENTTARGET = 'Linkbutton4'
        data = {'__VIEWSTATE': __VIEWSTATE, 'hidd_type': '1', '__EVENTVALIDATION': __EVENTVALIDATION,
                '__EVENTTARGET': __EVENTTARGET}
        page = Selector(response=response).xpath('//span[@id="lblPageCount"]/text()').extract_first()
        data['newpage'] = page
        yield scrapy.FormRequest(
            url='http://218.60.144.163/LNJGPublisher/corpinfo/CorpInfo.aspx',
            callback=self.parse,
            formdata=data,
            meta={'page': int(page)}
        )

    def parse(self, response):
        __VIEWSTATE = Selector(response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        __EVENTTARGET = 'Linkbutton2'
        div_under_table = Selector(response).xpath('//div[@class="list_container inner"]')
        data = {'__VIEWSTATE': __VIEWSTATE, 'hidd_type': '1', '__EVENTVALIDATION': __EVENTVALIDATION,
                '__EVENTTARGET': __EVENTTARGET}

        visible_province = div_under_table.xpath('./table/tbody/tr/td[3]/a/@onclick')
        for v in visible_province:
            company_name = v.extract()
            re_data = 'OpenCorpDetail\(\'(.*)\',\'(.*)\',\'(.*)\'\)'
            company_name = re.findall(re_data, company_name)
            rowGuid = company_name[0][0]
            CorpCode = company_name[0][1]
            CorpName = company_name[0][2]
            repeat = self.r.sadd('Company_name', CorpName)
            repeat = 1
            if repeat != 0:
                url = 'http://218.60.144.163/LNJGPublisher/corpinfo/' \
                      'CorpDetailInfo.aspx?rowGuid=%s&CorpCode=%s&' \
                      'CorpName=%s&VType=1' % (rowGuid, CorpCode, CorpName)
                yield scrapy.Request(url=url, callback=self.company_information, dont_filter=True)
            else:
                print('此公司信息已经存在', company_name)

        page = int(response.meta['page'])
        page -= 1
        self.number -= 1
        if page != 0:
            data['newpage'] = str(page)
            yield scrapy.FormRequest(url=self.url, callback=self.parse, formdata=data, dont_filter=True,
                                     meta={'page': page}
                                     )

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@class="name_level3"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@id="LicenseNum"]/text()').extract_first()
        company_name = company_name.split()[0]
        if number is not None:
            number = number.split()[0]
            number = number
        else:
            number = ''
        cc = 'http://218.60.144.163/LNJGPublisher/handle/Corp_Project.ashx?' \
             'CorpCode=%s&CorpName=%s&nPageCount=0&nPageIndex=1&nRecordSetCount=0&nPageSize=%s&_=1558580207472' \
             % (number, company_name, 100)
        yield scrapy.Request(url=cc, callback=self.project, meta={'companyName': company_name})

    def project(self, response):
        tr = templates.jilin_json_url_analysis(response, 2, state=True)
        for every_tr in tr:
            yield scrapy.Request(url=every_tr, callback=self.project_basic,
                                 meta={'companyName': response.meta['companyName']})

    def project_basic(self, response):
        basic = templates.Projects('Project')
        attrs = [{'that': '', 'attr': '//td[@colspan="3"]/text()', 'name': 'name'},
                 {'that': '', 'attr': '//td[@class="name_level3 col_01_value"]/text()', 'name': 'code'},
                 {'that': 0, 'attr': '//td[@class="col_02_value"]', 'name': 'provinceCode', 'then': 'text()'},
                 {'that': 1, 'attr': '//td[@class="col_01_value"]', 'name': 'unit', 'then': 'text()'},
                 {'that': 1, 'attr': '//td[@class="col_02_value"]', 'name': 'catalog', 'then': 'text()'},
                 {'that': 2, 'attr': '//td[@class="col_01_value"]', 'name': 'unitLicenseNum', 'then': 'text()'},
                 {'that': 2, 'attr': '//td[@class="col_02_value"]', 'name': 'area', 'then': 'text()'},
                 {'that': 4, 'attr': '//td[@class="col_01_value"]', 'name': 'docuCode', 'then': 'text()'},
                 {'that': 4, 'attr': '//td[@class="col_02_value"]', 'name': 'level', 'then': 'text()'},
                 {'that': 5, 'attr': '//td[@class="col_01_value"]', 'name': 'money', 'then': 'text()'},
                 {'that': 5, 'attr': '//td[@class="col_02_value"]', 'name': 'acreage', 'then': 'text()'},
                 {'that': 6, 'attr': '//td[@class="col_01_value"]', 'name': 'trait', 'then': 'text()'},
                 {'that': 6, 'attr': '//td[@class="col_02_value"]', 'name': 'purpose', 'then': 'text()'},
                 ]
        code = Selector(response=response).xpath('//td[@class="name_level3 col_01_value"]/text()').extract_first()
        name = Selector(response=response).xpath('//td[@colspan="3"]/text()').extract_first()
        code = code.split()[0]
        xx = 'PRJNUM=(.*)'
        basic_d = basic.html_analysis(response, attrs)
        basic_d['companyName'] = response.meta['companyName']

        basic = templates.Project(**basic_d)
        basic_data = basic.data()
        print(basic_data, '基本信息')
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                             body=json.dumps(basic_data), callback=self.project_zz,
                             headers={'Content-Type': 'application/json'}, method='POST',
                             meta={'type': '基本信息',
                                   'company_name': basic_data['companyName']
                                   },
                             )

        #
        bid_url = 'http://218.60.144.163/LNJGPublisher/handle/ProjectHandler.ashx?method=ztb&PRJNUM=%s&_=1558598717869' \
                  % re.findall(xx, response.url)[0]
        yield scrapy.Request(url=bid_url, callback=self.project_bid_list,
                             meta={'companyName': response.meta['companyName'], 'code': code})

        drawing_url = 'http://218.60.144.163/LNJGPublisher/handle/ProjectHandler.ashx?method=sgtsc&PRJNUM=%s&_=1558598717869' % \
                      re.findall(xx, response.url)[0]
        print(response.url, '施工图纸审查')
        yield scrapy.Request(url=drawing_url, callback=self.project_drawing_list,
                             meta={'companyName': response.meta['companyName'],
                                   'code': code})

        contract_url = 'http://218.60.144.163/LNJGPublisher/handle/ProjectHandler.ashx?method=htba&PRJNUM=%s&_=1558598717869' % \
                       re.findall(xx, response.url)[0]
        print(contract_url, '合同备案全部')
        yield scrapy.Request(url=contract_url, callback=self.project_contract_list,
                             meta={'companyName': response.meta['companyName'], 'code': code})

        construction_url = 'http://218.60.144.163/LNJGPublisher/handle/ProjectHandler.ashx?method=sgxk&PRJNUM=%s&_=1558598717869' % \
                           re.findall(xx, response.url)[0]
        print(construction_url, '施工许可详list')
        yield scrapy.Request(url=construction_url, callback=self.project_construction_list,
                             meta={'companyName': response.meta['companyName'], 'name': name})


    def project_bid_list(self, response):
        tr = templates.jilin_json_url_analysis(response, 8, big='http://218.60.144.163/LNJGPublisher')
        for every_tr in tr:
            yield scrapy.Request(url=every_tr, callback=self.bid_info,
                                 meta={'companyName': response.meta['companyName'], 'code': response.meta['code']})

    def project_drawing_list(self, response):
        tr = templates.jilin_json_url_analysis(response, 0, direct=True)
        for every_tr in tr:
            td = every_tr.xpath('./td')
            if td[1].xpath('text()'):
                censorNum = td[1].xpath('text()')[0]
            else:
                censorNum = ''

            if td[2].xpath('text()'):
                surveyCorpName = td[2].xpath('text()')[0]
            else:
                surveyCorpName = ''

            if td[3].xpath('text()'):
                designCorpName = td[3].xpath('text()')[0]
            else:
                designCorpName = ''

            if td[4].xpath('text()'):
                censorCorpName = td[4].xpath('text()')[0]
            else:
                censorCorpName = ''

            if td[5].xpath('text()'):
                censorEDate = td[5].xpath('text()')[0]
            else:
                censorEDate = ''
            drawing = templates.MakeDrawing(companyName=response.meta['companyName'],
                                            code=response.meta['code'],
                                            censorNum=censorNum, surveyCorpName=surveyCorpName,
                                            provinceCensorNum=censorNum,
                                            designCorpName=designCorpName, censorCorpName=censorCorpName,
                                            censorEDate=censorEDate
                                            )
            drawing_data = drawing.data()
            print(drawing_data, '施工图纸审查')
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectCensor.htm',
                                 body=json.dumps(drawing_data), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '施工图纸审查'}
                                 )

    def project_contract_list(self, response):
        tr = templates.jilin_json_url_analysis(response, 6, big='http://218.60.144.163/LNJGPublisher')
        for every_tr in tr:
            print(every_tr, '单个的合同备案')
            yield scrapy.Request(url=every_tr, callback=self.contract_info,
                                 meta={'companyName': response.meta['companyName'], 'code': response.meta['code']})

    def project_construction_list(self, response):
        tr = templates.jilin_json_url_analysis(response, 6, big='http://218.60.144.163/LNJGPublisher')
        for every_tr in tr:
            yield scrapy.Request(url=every_tr, callback=self.construction_info,
                                 meta={'companyName': response.meta['companyName'], 'name': response.meta['name']})

    # def project_completed_list(self, response):
    #     tr = templates.jilin_json_url_analysis(response, 7, 'http://218.60.144.163/LNJGPublisher')
    #     for every_tr in tr:
    #         print(every_tr, '竣工验收list')
    #         # yield scrapy.Request(url=every_tr, callback=self.comppleted_info,
    #         #                      meta={'companyName': response.meta['companyName'], 'name': response.meta['name']})

    def bid_info(self, response):
        attrs = [{'that': '', 'attr': '//span[@id="lblPrjNum"]/text()', 'name': 'code'},
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
        # print(response.text, response.meta['companyName'], response.meta['name'])
        bid_data = bid_object.html_analysis(response, attrs)
        bid_data['companyName'] = response.meta['companyName']
        bid_zz = templates.Mark(**bid_data)
        bid_zz = bid_zz.data()
        print(bid_zz, '招标信息')
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
                             body=json.dumps(bid_zz), callback=self.project_zz,
                             headers={'Content-Type': 'application/json'}, method='POST',
                             meta={'type': '招标信息'}
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
        print(contract_data, response.meta['companyName'], response.meta['code'])
        contract_zz = templates.Contract(**contract_data)
        contract_zz = contract_zz.data()
        print(contract_zz, '合同备案')
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectContract.htm',
                             body=json.dumps(contract_zz), callback=self.project_zz,
                             headers={'Content-Type': 'application/json'}, method='POST',
                             meta={'type': '合同备案'}
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
        print(construction_zz, '施工许可详细信息')
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectBuilderLicence.htm',
                             body=json.dumps(construction_zz), callback=self.project_zz,
                             headers={'Content-Type': 'application/json'}, method='POST',
                             meta={'type': '施工许可详细信息'}
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
    #     # yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
    #     #                      body=json.dumps(contract_zz), callback=self.project_zz,
    #  headers={'Content-Type': 'application/json'},method='POST'
    #     #                      )

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

