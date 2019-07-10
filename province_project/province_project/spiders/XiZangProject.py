# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
import re
from province_project import templates


class XiZangProvinceMax(scrapy.Spider):
    name = 'XiZangProvinceMax'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.index = 1
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://111.11.196.111/aspx/corpinfo/CorpInfo.aspx?corpname=&cert=&PageIndex=1'
        self.flag = True
        self.into = 'XX'
        self.number = 5
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://111.11.196.111'

    def start_requests(self):

        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        page = Selector(response=response).xpath('//span[@id="pagecountCtrl"]/text()').extract_first()
        yield scrapy.Request(url='http://111.11.196.111/aspx/corpinfo/CorpInfo.aspx?'
                                 'corpname=&cert=&PageIndex=%s' % int(page),
                             callback=self.parse,
                             meta={'page': page}
                             )

    def parse(self, response):
        a_href_all = Selector(response=response).xpath('//table[@class="table table-striped table-bordered"]'
                                                       '/tbody/tr/td[2]/a/@href')
        for t in a_href_all:
            a_url = t.extract()
            a_url = a_url.split('../..')[1]
            re_a = self.bigurl + a_url
            # print(re_a)
            yield scrapy.Request(url=re_a, callback=self.company_information)
        page = int(response.meta['page'])
        page -= 1
        self.number -= 1
        if page != 0:
            yield scrapy.Request(url='http://111.11.196.111/aspx/corpinfo/CorpInfo.aspx?'
                                     'corpname=&cert=&PageIndex=%s' % page,
                                 callback=self.parse,
                                 meta={'page': page}
                                 )

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@id="corpname"]/text()').extract_first()
        repeat = self.r.sadd('Company_name', company_name + '西藏自治区')
        repeat = 1
        if repeat != 0:
            licenseNum = Selector(response=response).xpath('//td[@id="corpcode"]/text()').extract_first()
            contactMan = Selector(response=response).xpath('//td[@id="linkman"]/text()').extract_first()
            address = Selector(response=response).xpath('//td[@id="address"]/text()').extract_first()
            province = Selector(response=response).xpath('//td[@id="province"]/text()').extract_first()
            project_list = Selector(response=response).xpath(
                '//div[@id="company_info_projects"]/table/tbody/tr/td[3]/@title')
            for p in project_list:
                project_name = p.extract()
                yield scrapy.Request(
                    url='http://111.11.196.111/aspx/projectsinfo/projectsinfo.aspx?prjname=%s&PageIndex=1' % project_name,
                    callback=self.project_list, meta={'companyName': company_name}
                )

    def project_list(self, response):
        print(response.url)
        url = Selector(response=response).xpath(
            '//table[@class="table table-striped table-bordered"]/tbody/tr/td/a/@href')
        for u in url:
            u = u.extract()
            u = u.replace('../..', 'http://111.11.196.111')
            yield scrapy.Request(url=u, callback=self.project, meta={'companyName': response.meta['companyName']})

    def project(self, response):
        basic = templates.Projects('Project')
        attrs = [
            {'that': '', 'attr': '//td[@id="lblPrjName"]/text()', 'name': 'name'},
            {'that': '', 'attr': '//td[@id="lblPrjNum"]/text()', 'name': 'code'},
            {'that': '', 'attr': '//td[@id="lblPrjNum"]/text()', 'name': 'provinceCode'},
            {'that': '', 'attr': '//td[@id="lblPrjTypeNum"]/text()', 'name': 'catalog'},
            {'that': '', 'attr': '//td[@id="lblBuildCorpName"]/text()', 'name': 'unit'},
            {'that': '', 'attr': '//td[@id="lblBuildCorpCode"]/text()', 'name': 'unitLicenseNum'},
            {'that': '', 'attr': '//td[@id="lblCountyNum"]/text()', 'name': 'area'},
            {'that': '', 'attr': '//td[@id="lblPrjApprovalNum"]/text()', 'name': 'docuCode'},
            {'that': '', 'attr': '//td[@id="lblPrjApprovalLevelNum"]/text()', 'name': 'level'},
            {'that': '', 'attr': '//td[@id="lblAllInvest"]/text()', 'name': 'money'},
            {'that': '', 'attr': '//td[@id="lblAllArea"]/text()', 'name': 'acreage'},
            {'that': '', 'attr': '//td[@id="lblPrjPropertyNum"]/text()', 'name': 'trait'},
            {'that': '', 'attr': '//td[@id="lblPrjFunctionNum"]/text()', 'name': 'purpose'},
        ]
        basic_text = basic.html_analysis(response=response, attrs=attrs)
        basic_text['companyName'] = response.meta['companyName']
        if basic_text['level'] == '暂无':
            basic_text['level'] = ''
        basic_data = templates.Project(**basic_text)
        basic_data = basic_data.data()
        print('基本信息', '*******************************', basic_data)
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                             body=json.dumps(basic_data), callback=self.project_zz,
                             headers={'Content-Type': 'application/json'}, method='POST',
                             meta={'type': '基本信息', 'company_name': basic_data['companyName']}
                             )
        #
        bid_list = Selector(response=response).xpath('//div[@id="project_step1"]/table/tbody/tr')
        for b in bid_list:
            tenderClass = b.xpath('./td[2]/text()').extract_first()
            tenderType = b.xpath('./td[3]/text()').extract_first()
            tenderCorpName = b.xpath('./td[4]/a/text()').extract_first()
            tenderResultDate = b.xpath('./td[5]/text()').extract_first()
            tenderMoney = b.xpath('./td[6]/text()').extract_first()
            tenderNum = b.xpath('./td[7]/a/text()').extract_first()
            bid_data = templates.Mark(tenderClass=tenderClass, tenderType=tenderType, tenderCorpName=tenderCorpName,
                                      tenderResultDate=tenderResultDate, tenderMoney=tenderMoney, tenderNum=tenderNum,
                                      provinceTenderNum=tenderNum, code=basic_data['code'],
                                      companyName=response.meta['companyName']
                                      )
            bid_data = bid_data.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
                                 body=json.dumps(bid_data), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '招标信息',}
                                 )
            # print('招标信息', '*******************************', bid_data)

        drawing_list = Selector(response=response).xpath('//div[@id="project_step2"]/table/tbody/tr')
        for d in drawing_list:
            censorNum = d.xpath('./td[2]/text()').extract_first()
            provinceCensorNum = d.xpath('./td[3]/text()').extract_first()
            surveyCorpName = d.xpath('./td[4]/a/text()').extract_first()
            designCorpName = d.xpath('./td[5]/a/text()').extract_first()
            censorCorpName = d.xpath('./td[6]/a/text()').extract_first()
            censorEDate = d.xpath('./td[7]/a/text()').extract_first()
            drawing_data = templates.MakeDrawing(censorNum=censorNum, provinceCensorNum=provinceCensorNum,
                                                 surveyCorpName=surveyCorpName,
                                                 designCorpName=designCorpName, censorCorpName=censorCorpName,
                                                 censorEDate=censorEDate, code=basic_data['code'],
                                                 companyName=response.meta['companyName']
                                                 )
            drawing_data = drawing_data.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectCensor.htm',
                                 body=json.dumps(drawing_data), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '施工图纸审查', }
                                 )
            print('施工图纸审查', '*******************************', drawing_data)

        contract_list = Selector(response=response).xpath('//div[@id="project_step3"]/table/tbody/tr')
        for d in contract_list:
            contractType = d.xpath('./td[2]/text()').extract_first()
            recordNum = d.xpath('./td[3]/text()').extract_first()
            provinceRecordNum = d.xpath('./td[4]/text()').extract_first()
            contractMoney = d.xpath('./td[5]/text()').extract_first()
            contractDate = d.xpath('./td[6]/text()').extract_first()
            contract_data = templates.Contract(contractType=contractType, recordNum=recordNum,
                                               provinceRecordNum=provinceRecordNum,
                                               contractMoney=contractMoney,
                                               contractDate=contractDate, code=basic_data['code'],
                                               companyName=response.meta['companyName']
                                               )
            contract_data = contract_data.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectContract.htm',
                                 body=json.dumps(contract_data), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '合同备案', }

                                 )
            print('合同备案', '*******************************', contract_data)
        print(response.url, 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

        construction_list = Selector(response=response).xpath('//div[@id="project_step4"]/table/tbody/tr')
        for d in construction_list:
            builderLicenceNum = d.xpath('./td[2]/text()').extract_first()
            consCorpName = d.xpath('./td[3]/a/text()').extract_first()
            contractMoney = d.xpath('./td[4]/text()').extract_first()
            area = d.xpath('./td[5]/text()').extract_first()
            createDate = d.xpath('./td[6]/text()').extract_first()
            construction_data = templates.ConstructionPermit(builderLicenceNum=builderLicenceNum, provinceBuilderLicenceNum=builderLicenceNum,
                                                             consCorpName=consCorpName,
                                                             contractMoney=contractMoney,
                                                             area=area, code=basic_data['code'],
                                                             createDate=createDate,
                                                             companyName=response.meta['companyName']
                                                             )
            construction_data = construction_data.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectBuilderLicence.htm',
                                 body=json.dumps(construction_data), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '施工许可', }
                                 )
            print('施工许可', '*******************************', construction_data)

        completion_list = Selector(response=response).xpath('//div[@id="project_step4"]/table/tbody/tr')
        for c in completion_list:
            prjFinishNum = c.xpath('./td[2]/text()').extract_first()
            provincePrjFinishNum = c.xpath('./td[3]/a/text()').extract_first()
            factCost = c.xpath('./td[4]/text()').extract_first()
            factArea = c.xpath('./td[5]/text()').extract_first()
            factBeginDate = c.xpath('./td[6]/text()').extract_first()
            factEndDate = c.xpath('./td[6]/text()').extract_first()
            completion_data = templates.Completion(prjFinishNum=prjFinishNum,
                                                   provincePrjFinishNum=provincePrjFinishNum,
                                                   factCost=factCost,
                                                   factArea=factArea,
                                                   factBeginDate=factBeginDate,
                                                   code=basic_data['code'],
                                                   factEndDate=factEndDate,
                                                   companyName=response.meta['companyName']
                                                   )
            completion_data = completion_data.data()
            yield scrapy.Request(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectFinish.htm',
                body=json.dumps(completion_data), callback=self.project_zz,
                headers={'Content-Type': 'application/json'}, method='POST',
                meta={'type': '竣工验收', }
            )
            print('竣工验收', '*******************************', completion_data)

    def project_zz(self, response):
        not_company_code = json.loads(response.text)['code']
        if not_company_code == -102 and response.meta['type'] == '基本信息':
            not_search_company_name = response.meta['company_name']
            self.r.sadd('title_name1', not_search_company_name)
            print('正在添加公司基本信息', not_search_company_name)
        else:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>%s------%s' % (response.text, response.meta['type'],))