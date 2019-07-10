# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
from province_project import templates

heads = {'Accept': 'text/html, */*; q=0.01',
         'Accept-Encoding': 'gzip, deflate',
         'Accept-Language': 'zh-CN,zh;q=0.9',
         'Connection': 'keep-alive',
         'Host': '115.29.2.37:8080',
         'Origin': 'http://115.29.2.37:8080',
         'Referer': 'http://115.29.2.37:8080/enterprise.php',
         'X-Requested-With': 'XMLHttpRequest',
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'
         }


class ZhaoJiangProject(scrapy.Spider):
    name = 'ZhaoJiangProject'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://115.29.2.37:8080/enterprise_ajax.php'
        self.index = 1
        self.flag = True
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.company_url = 'http://115.29.2.37:8080/'

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        tr = Selector(response=response).xpath('//table[@class="t1"]/tr')
        zzz = Selector(response=response).xpath('//span[@class="vcountPage"]/text()').extract_first()
        tr = tr[1:-1]
        for t in tr:
            td = t.xpath('./td')
            url = td[1].xpath('./div/a/@href').extract_first()
            url = 'http://115.29.2.37:8080/' + url
            yield Request(url=url, callback=self.company_information,
                          dont_filter=True,
                          headers=heads
                          )
        self.index = self.index + 1
        page = Selector(response=response).xpath('//div[@id="pagebar"]/ul/li[3]/@alt').extract_first()
        if self.index != int(zzz):
            yield scrapy.FormRequest(url=self.url,
                                     callback=self.parse,
                                     dont_filter=True,
                                     formdata={'page': page},
                                     headers=heads,
                                     )

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@colspan="5"]/text()')[0].extract()
        a_url = Selector(response=response).xpath('//tr[@class="auto_h"]/td/div/a/@href')
        for a in a_url:
            url = 'http://115.29.2.37:8080/' + a.extract()
            yield scrapy.Request(url=url, callback=self.project, meta={'companyName': company_name}, headers=heads)

    def project(self, response):
        basic_info = templates.Projects('Project')
        attrs = [
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[1]/td[2]/text()', 'name': 'name'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[2]/td[2]/text()', 'name': 'code'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[2]/td[2]/text()', 'name': 'provinceCode'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[3]/td[2]/text()', 'name': 'unit'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[3]/td[4]/text()', 'name': 'catalog'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[4]/td[2]/text()', 'name': 'unitLicenseNum'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[4]/td[4]/text()', 'name': 'area'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[6]/td[2]/text()', 'name': 'docuCode'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[6]/td[4]/text()', 'name': 'level'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[7]/td[2]/text()', 'name': 'money'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[7]/td[4]/text()', 'name': 'acreage'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[8]/td[2]/text()', 'name': 'trait'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[8]/td[4]/text()', 'name': 'purpose'},

        ]
        basic_data = basic_info.html_analysis(response, attrs)
        basic_data['companyName'] = response.meta['companyName']
        basic = templates.Project(**basic_data)
        b_data = basic.data()
        print(b_data, '基本信息', b_data['companyName'])
        yield scrapy.Request(
            # url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
            url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
            body=json.dumps(b_data),
            callback=self.project_zz,
            headers={'Content-Type': 'application/json'}, method='POST',
            meta={'type': '基本信息', 'company_name': b_data['companyName']}
        )

        bid_url = Selector(response=response).xpath('//div[@class="classContent t1"]/table/tr')
        bid_url = bid_url[1:]
        for b in bid_url:
            a = b.xpath('./td[7]/a/@href').extract_first()
            a = 'http://115.29.2.37:8080/' + a
            yield scrapy.Request(url=a, callback=self.bid_info, headers=heads,
                                 meta={'companyName': response.meta['companyName']}
                                 )

        drawing_info = Selector(response=response).xpath('//div[@class="classContent t2"]/table/tr')
        drawing_info = drawing_info[1:]
        print(len(drawing_info), '施工图纸审查----bbbbbbbbbbbbbbbbbbbbbbbbbbbbb', response.url)
        for d in drawing_info:
            censorNum = d.xpath('./td[2]/text()').extract_first()
            surveyCorpName = d.xpath('./td[3]/text()').extract_first()
            designCorpName = d.xpath('./td[4]/text()').extract_first()
            censorCorpName = d.xpath('./td[5]/text()').extract_first()
            censorEDate = d.xpath('./td[6]/text()').extract_first()
            drawing_data = templates.MakeDrawing(censorNum=censorNum, surveyCorpName=surveyCorpName,
                                                 designCorpName=designCorpName, censorCorpName=censorCorpName,
                                                 censorEDate=censorEDate
                                                 )
            drawing_data = drawing_data.data()
            print(drawing_data, '施工图纸审查')
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectCensor.htm',
                                 body=json.dumps(drawing_data),
                                 callback=self.project_zz,
                                 headers={'Content-Type': 'application/json'}, method='POST',
                                 meta={'type': '施工图纸审查'}
                                 )
        contract_list = Selector(response=response).xpath('//div[@class="classContent t3"]/table/tr')
        contract_list = contract_list[1:]
        for c in contract_list:
            print(c.xpath('./td[6]/a/@href').extract_first(), '合同备案url')
            u = 'http://115.29.2.37:8080/' + c.xpath('./td[6]/a/@href').extract_first()
            yield scrapy.Request(url=u, callback=self.contract_info,
                                 meta={'companyName': response.meta['companyName']})

        construction_list = Selector(response=response).xpath('//div[@class="classContent t4"]/table/tr/td/a/@href')
        for c in construction_list:
            u = 'http://115.29.2.37:8080/' + c.extract()
            yield scrapy.Request(url=u, callback=self.construction_info,
                                 meta={'companyName': response.meta['companyName']})

        finish_list = Selector(response=response).xpath('//div[@class="classContent t5"]/table/tr/td/a/@href')
        for f in finish_list:
            u = 'http://115.29.2.37:8080/' + f.extract()
            yield scrapy.Request(url=u, callback=self.finish_info,
                                 meta={'companyName': response.meta['companyName']})

    def bid_info(self, response):
        attrs = [
            {'that': '', 'attr': '//table[@width="100%"]/tr[3]/td[2]/text()', 'name': 'code'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[10]/td[2]/text()', 'name': 'tenderNum'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[10]/td[2]/text()', 'name': 'provinceTenderNum'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[11]/td[2]/text()', 'name': 'tenderClass'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[11]/td[4]/text()', 'name': 'tenderType'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[12]/td[2]/text()', 'name': 'tenderResultDate'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[12]/td[4]/text()', 'name': 'tenderMoney'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[13]/td[2]/text()', 'name': 'prjSize'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[13]/td[4]/text()', 'name': 'area'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[14]/td[2]/a/@title', 'name': 'agencyCorpName'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[14]/td[4]/text()', 'name': 'agencyCorpCode'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[15]/td[2]/a/text()', 'name': 'tenderCorpName'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[15]/td[4]/text()', 'name': 'tenderCorpCode'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[16]/td[2]/a/text()', 'name': 'constructorName'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[16]/td[4]/text()', 'name': 'constructorIDCard'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[17]/td[2]/a/text()', 'name': 'createDate'},

        ]
        bid = templates.Projects('Mark')
        bid_zz = bid.html_analysis(response=response, attrs=attrs)
        bid_zz['companyName'] = response.meta['companyName']
        bid_data = templates.Mark(**bid_zz)
        bid_data = bid_data.data()
        print(bid_data, '招标信息')
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                             body=json.dumps(bid_data),
                             callback=self.project_zz,
                             headers={'Content-Type': 'application/json'}, method='POST',
                             meta={'type': '招标信息'}
                             )

    def contract_info(self, response):
        attrs = [
            {'that': '', 'attr': '//table[@width="100%"]/tr[3]/td[2]/text()', 'name': 'code'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[10]/td[2]/text()', 'name': 'recordNum'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[10]/td[2]/text()', 'name': 'provinceRecordNum'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[12]/td[2]/text()', 'name': 'contractType'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[12]/td[4]/text()', 'name': 'contractMoney'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[13]/td[2]/text()', 'name': 'prjSize'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[13]/td[4]/text()', 'name': 'contractDate'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[14]/td[2]/a/@title', 'name': 'proprietorCorpName'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[14]/td[4]/text()', 'name': 'proprietorCorpCode'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[15]/td[2]/a/text()', 'name': 'contractorCorpName'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[15]/td[4]/text()', 'name': 'contractorCorpCode'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[16]/td[2]/a/text()', 'name': 'unionCorpName'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[16]/td[4]/text()', 'name': 'unionCorpCode'},
            {'that': '', 'attr': '//table[@width="100%"]/tr[17]/td[2]/a/text()', 'name': 'createDate'},

        ]
        contract = templates.Projects('Contract')
        contract = contract.html_analysis(response=response, attrs=attrs)
        contract['companyName'] = response.meta['companyName']
        contract_data = templates.Contract(**contract)
        contract_data = contract_data.data()
        print(contract_data, '合同信息')
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectContract.htm',
                             body=json.dumps(contract_data),
                             callback=self.project_zz,
                             headers={'Content-Type': 'application/json'}, method='POST',
                             meta={'type': '合同信息'}
                             )

    def construction_info(self, response):
        attrs = [
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[3]/td[2]/text()', 'name': 'code'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[10]/td[2]/text()', 'name': 'builderLicenceNum'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[10]/td[2]/text()',
             'name': 'provinceBuilderLicenceNum'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[11]/td[2]/text()', 'name': 'censorNum'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[11]/td[4]/text()', 'name': 'contractMoney'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[12]/td[2]/a/@title', 'name': 'constructorName'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[12]/td[4]/text()', 'name': 'constructorIDCard'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[13]/td[2]/a/text()', 'name': 'supervisionName'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[13]/td[4]/text()', 'name': 'supervisionIDCard'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[14]/td[2]/text()', 'name': 'area'},
            {'that': '', 'attr': '//div[@class="detail_list"]/table/tr[14]/td[4]/text()', 'name': 'createDate'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[2]/td[3]/a/text()',
             'name': 'designCorpName'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[2]/td[4]/text()', 'name': 'designCorpCode'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[2]/td[5]/text()', 'name': 'designCorpArea'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[3]/td[3]/a/text()', 'name': 'econCorpName'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[3]/td[4]/text()', 'name': 'econCorpCode'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[3]/td[5]/text()', 'name': 'econCorpArea'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[4]/td[3]/a/text()', 'name': 'consCorpName'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[4]/td[4]/text()', 'name': 'consCorpCode'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[4]/td[5]/text()', 'name': 'consCorpArea'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[5]/td[3]/a/text()', 'name': 'superCorpName'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[5]/td[4]/text()', 'name': 'superCorpCode'},
            {'that': '', 'attr': '//div[@class="classContent t1"]/table/tr[5]/td[5]/text()', 'name': 'superCorpArea'},

        ]
        construction = templates.Projects('ConstructionPermit')
        construction = construction.html_analysis(response=response, attrs=attrs)
        construction['companyName'] = response.meta['companyName']
        construction_data = templates.ConstructionPermit(**construction)
        print(construction_data.data(), '施工许可信息录入')
        contract_data = construction_data.data()
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectBuilderLicence.htm',
                             body=json.dumps(contract_data),
                             callback=self.project_zz, method='POST',
                             headers={'Content-Type': 'application/json'},
                             meta={'type': '施工许可信息录入'}
                             )

    def finish_info(self, response):
        attrs = [
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[3]/td[2]/text()',
             'name': 'code'},
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[10]/td[2]/text()',
             'name': 'prjFinishNum'},
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[10]/td[2]/text()',
             'name': 'provincePrjFinishNum'},
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[11]/td[2]/text()',
             'name': 'factCost'},
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[11]/td[4]/text()',
             'name': 'factArea'},
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[12]/td[2]/text()',
             'name': 'factSize'},
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[13]/td[2]/text()',
             'name': 'factBeginDate'},
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[13]/td[4]/text()',
             'name': 'factEndDate'},
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[14]/td[2]/text()',
             'name': 'createDate'},
            {'that': '', 'attr': '//div[@class="detail"][1]/div[@class="detail_list"]/table/tr[14]/td[4]/text()',
             'name': 'mark'},
        ]
        finish = templates.Projects('Completion')
        finish = finish.html_analysis(response=response, attrs=attrs)
        finish['companyName'] = response.meta['companyName']
        finish_data = templates.Completion(**finish)
        print(finish_data.data(), '竣工')
        contract_data = finish_data.data()
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectFinish.htm',
                             body=json.dumps(contract_data),
                             callback=self.project_zz, method='POST',
                             headers={'Content-Type': 'application/json'},
                             meta={'type': '竣工'}
                             )

    def project_zz(self, response):
        not_company_code = json.loads(response.text)['code']
        if not_company_code == -102 and response.meta['type'] == '基本信息':
            not_search_company_name = response.meta['company_name']
            self.r.sadd('title_name1', not_search_company_name)
            print('正在添加公司基本信息', not_search_company_name)
        else:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>%s------%s' % (response.text, response.meta['type'],))
