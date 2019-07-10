# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import time
import json
import re
from province_project import templates


class ShanDongProject(scrapy.Spider):
    name = 'ShanDongProject'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.index = 1
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        now_time = time.time() * 1000
        now_time = int(now_time)
        reduce_time = now_time - 964344
        self.number = 5
        self.url = 'http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback=jQuery17109359142758390728_%s&methodname=GetCorpInfo&CorpName=&CorpCode=&CertType=&LegalMan=&CurrPageIndex=%s&PageSize=%s&' % (
            reduce_time, 1, 12)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {'licenseNum': '', 'contactMan': '', 'area': '', 'companyArea': '山东省', 'contactAddress': '',
                     'contactPhone': '', 'token': self.token}
        self.flag = True

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        page = (int(json_data['data']['TotalNum']) // 12) + 1
        print(page)
        now_time = time.time() * 1000
        now_time = int(now_time)
        time.sleep(0.5)
        reduce_time = now_time - 964344
        yield scrapy.Request(
            url='http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?'
                'callback=jQuery17106733853342277394_%s&methodname='
                'GetCorpInfo&CorpName=&CorpCode=&CaertType=&LegalMan=&'
                'CurrPageIndex=%s&PageSize=12&_=1557275666418' % (reduce_time, page),
            callback=self.parse,
            meta={'page': int(page)}
        )

    def parse(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        now_time = time.time() * 1000
        now_time = int(now_time)
        time.sleep(0.5)
        reduce_time = now_time - 964344
        for i in json_data['data']['CorpInfoList']:
            number = i['CorpCode']
            companyName = i['CorpName']
            u = 'http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?' \
                'callback=jQuery17108153653090248525_%s&methodname=GetParticipationProjectInfo&CorpCode=%s&IDCard=&CurrPageIndex=1&PageSize=1000' % (
                    reduce_time, number)
            yield scrapy.Request(url=u, callback=self.project,
                                 meta={'companyName': companyName,
                                       'number': number, 'reduce_time': reduce_time})
        page = int(response.meta['page']) - 1
        # self.number -= 1
        if page != 0:
            yield scrapy.Request(
                url='http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback='
                    'jQuery17109359142758390728_%s&methodname=GetCorpInfo&CorpName=&CorpCode=&CertType=&LegalMan=&CurrPageIndex=%s&PageSize=%s&' % (
                        reduce_time, page, 12), callback=self.parse,
                meta={'page': page}
            )

    def project(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        now_time = time.time() * 1000
        now_time = int(now_time)
        time.sleep(0.5)
        reduce_time = now_time - 965344
        for i in json_data['data']['ProjectInfoList']:
            basic_url = 'http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?' \
                'callback=jQuery171007243400914259279_%s&methodname=GetProjectInfo&' \
                'ProjectNum=%s&ProjectName=&CityCode=&ProjectType=&BuildCorp=&ConsCorp=&' \
                'Constructor=&Supervision=&CurrPageIndex=1&PageSize=1&TopNum=1&_=%s' % (
                    reduce_time, i['ProjectNum'], reduce_time)
            yield scrapy.Request(url=basic_url, callback=self.basic, meta={'companyName': response.meta['companyName']})

            bid_url = 'http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback=jQuery17104192270770537856_%s&methodname=GetPrjTenderInfo&CurrPageIndex=1&PageSize=1000&PrjNum=%s&_=%s'% (
                    reduce_time, i['ProjectNum'], reduce_time)
            yield scrapy.Request(url=bid_url, callback=self.bid, method='POST',
                                 meta={'companyName': response.meta['companyName']})

            drawing_url = 'http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback=jQuery17103056221269708761_%s&methodname=GetProjectCensorInfo&CurrPageIndex=1&PageSize=1000&PrjNum=%s&_=%s' % (
                reduce_time, i['ProjectNum'], reduce_time)
            yield scrapy.Request(url=drawing_url, callback=self.drawing,
                                 meta={'companyName': response.meta['companyName']})

            contract_url = 'http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback=jQuery17107196422576824613_%s&methodname=GetContractRecordInfo&CurrPageIndex=1&PageSize=1000&PrjNum=%s&_=%s' % (
                reduce_time, i['ProjectNum'], reduce_time)
            yield scrapy.Request(url=contract_url, callback=self.contract,
                                 meta={'companyName': response.meta['companyName']})

            construction_url = 'http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback=jQuery17107196422576824613_%s&methodname=GetBuilderLicenceInfo&CurrPageIndex=1&PageSize=5&PrjNum=%s&CertNO=0&_=%s' % (
                reduce_time, i['ProjectNum'], reduce_time)
            yield scrapy.Request(url=construction_url, callback=self.construction,
                                 meta={'companyName': response.meta['companyName']})
            #
            completed_url = 'http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback=jQuery17107196422576824613_%s&methodname=GetProjectFinishInfo&CurrPageIndex=1&PageSize=1000&PrjNum=%s&_=%s' % (
                reduce_time, i['ProjectNum'], reduce_time)
            yield scrapy.Request(url=completed_url, callback=self.completed,
                                 meta={'companyName': response.meta['companyName']})

    def basic(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        data = json_data['data']['ProjectInfoList'][0]
        basic = templates.Project(companyName=response.meta['companyName'],
                                  name=data['ProjectName'], code=data['ProjectNum'], provinceCode=data['ProjectNum'],
                                  area=data['AreaName'], unit=data['BuildCorpName'],
                                  unitLicenseNum=data['BuildCorpCode'],
                                  catalog=data['ProjectType'], acreage=data['AreaCode'],
                                  level=data['PrjApprovalLevelNum'],
                                  money=data['AllInvest'], trait=data['PrjPropertyNum'],
                                  docuCode=data['PrjApprovalNum'],
                                  purpose=data['ProjectType']
                                  )
        basic_data = basic.data()
        if basic_data['ProjectName'] or basic_data['ProjectNum']:
            print(basic_data, '基本信息')
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                                 body=json.dumps(basic_data), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '基本信息', 'company_name': basic_data['companyName']}
                                 )

    def bid(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        data = json_data['data']['TenderInfoList']
        for d in data:
            bid = templates.Mark(companyName=response.meta['companyName'], tenderNum=d['TenderNum'],
                                 code=d['PrjNum'],
                                 provinceTenderNum=d['TenderNum'], tenderResultDate=d['TenderResultDate'],
                                 tenderType=d['TenderType'], tenderClass=d['TenderClass'],
                                 tenderMoney=d['TenderMoney'],
                                 )
            bid_data = bid.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                                 body=json.dumps(bid_data), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '招标'}
                                 )

    def drawing(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        data = json_data['data']['ProjectCensorInfoList']
        for d in data:
            drawing_info = templates.MakeDrawing(companyName=response.meta['companyName'], code=d['PrjNum'],
                                                 censorNum=d['CensorNum'], provinceCensorNum=d['CensorNum'],
                                                 censorEDate=d['CensorEDate'], censorCorpName=d['CensorCorpName'],
                                                 censorCorpCode=d['CensorCorpCode'], surveyCorpName=d['EconCorpName'],
                                                 surveyCorpCode=d['EconCorpCode'], designCorpName=d['DesignCorpName'],
                                                 designCorpCode=d['DesignCorpCode']
                                                 )
            print(drawing_info.data(), '施工图审查')
            drawing_data = drawing_info.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectCensor.htm',
                                 body=json.dumps(drawing_data), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '施工图审查'}
                                 )

    def contract(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        data = json_data['data']['ContractRecordInfoList']
        for d in data:
            contract_info = templates.Contract(companyName=response.meta['companyName'], code=d['PrjNum'],
                                               recordNum=d['ContractNum'], provinceRecordNum=d['ContractNum'],
                                               contractClassify=d['ContractType'], contractMoney=d['ContractMoney'],
                                               contractDate=d['ContractDate']
                                               )
            print(contract_info.data(), '合同备案')
            drawing_data = contract_info.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectContract.htm',
                                 body=json.dumps(drawing_data), callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '合同备案'}
                                 )

    def construction(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        data = json_data['data']['BuilderLicenceInfoList']
        for d in data:
            builderLicenceNum = d['SingleProjectNO']
            builderLicenceNum = builderLicenceNum.replace('</br>', '')
            construction_info = templates.ConstructionPermit(companyName=response.meta['companyName'], code=d['PrjNum'],
                                                             builderLicenceNum=builderLicenceNum,
                                                             provinceBuilderLicenceNum=builderLicenceNum,
                                                             contractMoney=d['ContractPrice'],
                                                             area=d['ConstructionScale'], createDate=d['CertPrintDate'],
                                                             econCorpName=d['SurveyCorpName'],
                                                             econCorpCode=d['SurveyCorpCode'],
                                                             designCorpName=d['DesignCorpName'],
                                                             designCorpCode=d['DesignCorpCode'],
                                                             consCorpName=d['ConstructionCorpName'],
                                                             consCorpCode=d['ConstructionCorpCode'],
                                                             superCorpName=d['SupervisionCorpName'],
                                                             superCorpCode=d['SupervisionCorpCode']

                                                             )
            print(construction_info.data(), '施工许可')
            construction_data = construction_info.data()
            yield scrapy.Request(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectBuilderLicence.htm',
                body=json.dumps(construction_data), callback=self.project_zz,
                headers={'Content-Type': 'application/json'}, method='POST',
                meta={'type': '施工许可'}
                )

    def completed(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        data = json_data['data']['ProjectFinishInfoList']
        for d in data:
            completed_info = templates.Completion(companyName=response.meta['companyName'], code=d['PrjNum'],
                                                  prjFinishNum=d['PrjFinishNum'],
                                                  provincePrjFinishNum=d['PrjFinishNum'],
                                                  factCost=d['FactCost'], factArea=d['FactArea'],
                                                  factBeginDate=d['BDate'], factEndDate=d['EDate'],
                                                  )
            print(completed_info.data(), '竣工验收')
            completed_data = completed_info.data()
            yield scrapy.Request(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectFinish.htm',
                body=json.dumps(completed_data), callback=self.project_zz,
                headers={'Content-Type': 'application/json'}, method='POST',
                meta={'type': '竣工验收'}
            )

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
