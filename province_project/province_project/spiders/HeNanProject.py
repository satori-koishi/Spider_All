# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import random
import json
from province_project import templates


class HeNanProject(scrapy.Spider):
    name = 'HeNanProject'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.bigurl = 'http://hngcjs.hnjs.gov.cn'
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://hngcjs.hnjs.gov.cn/SiKuWeb/QiyeList.aspx?type=qyxx&val='
        self.index = 1
        self.flag = True
        self.number = 5
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {'area': '', 'companyArea': '河南省', 'contactMan': '', 'contactPhone': '', 'contactAddress': '',
                     'licenseNum': '', 'token': self.token}

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        page = Selector(response=response).xpath('//div[@id="AspNetPager2"]/ul/li')[12].xpath(
            './a/text()').extract_first()
        print(page, 'AAAAAAAAAA')
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        post_data = {'__VIEWSTATE': __VIEWSTATE, '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                     '__EVENTVALIDATION': __EVENTVALIDATION, '__EVENTTARGET': 'AspNetPager2', 'CretType': '全部企业类别',
                     '__EVENTARGUMENT': page}
        yield scrapy.FormRequest(url='http://hngcjs.hnjs.gov.cn/SiKuWeb/QiyeList.aspx?type=qyxx&val=',
                                 formdata=post_data,
                                 callback=self.parse,
                                 meta={'page': page}
                                 )

    def parse(self, response):
        post_data = {}
        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        post_data['__VIEWSTATE'] = __VIEWSTATE
        post_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
        post_data['__EVENTVALIDATION'] = __EVENTVALIDATION
        post_data['__EVENTTARGET'] = 'AspNetPager2'
        post_data['CretType'] = '全部企业类别'
        tr = Selector(response=response).xpath('//a[@target="_blank"]/@href')
        for t in tr:
            company_url = t.extract()
            yield scrapy.Request(url=self.bigurl + company_url, callback=self.company_information)
        page = int(response.meta['page'])
        page -= 1
        post_data['__EVENTARGUMENT'] = str(page)
        self.number -= 1
        if page != 0:
            yield scrapy.FormRequest(url='http://hngcjs.hnjs.gov.cn/SiKuWeb/QiyeList.aspx?type=qyxx&val=',
                                     formdata=post_data,
                                     callback=self.parse,
                                     meta={'page': page}
                                     )

    def company_information(self, response):
        company_name = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label10"]/text()').extract_first()
        number = Selector(response=response).xpath('//td[@class="inquiry_intitleb"]')[5] \
            .xpath('./span/text()').extract_first()
        if number is not None:
            number = number.split()[0]
            if len(number) == 18:
                number = number
            else:
                number = ''
        company_name = company_name.split()[0]
        xx = 'http://hngcjs.hnjs.gov.cn/SiKuWeb/Gcxm.aspx?CorpName=%s&CorpCode=%s' % (company_name, number)
        print(xx)
        yield scrapy.Request(url=xx,
                             callback=self.project,
                             meta={'company_name': company_name, 'number': number, 'page': 1}
                             )

    def project(self, response):
        url = Selector(response=response).xpath('//tr[@style="text-align: center;"]/td[4]/a/@href')
        for u in url:
            info = u.extract()
            project_url = 'http://hngcjs.hnjs.gov.cn' + info
            yield scrapy.Request(url=project_url, callback=self.info,
                                 meta={'company_name': response.meta['company_name'],
                                       'number': response.meta['number']})

        __VIEWSTATE = Selector(response=response).xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()

        __VIEWSTATEGENERATOR = Selector(response=response).xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()

        __EVENTVALIDATION = Selector(response=response).xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        page = int(response.meta['page'])
        page += 1
        cc = Selector(response=response).xpath('//ul/li/a')
        last_page = cc[-1]
        xx = last_page.xpath('@disabled').extract_first()
        print(xx, '--------%s' % page)
        if xx != 'disabled':
            post_data = {'__VIEWSTATE': __VIEWSTATE, '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                         '__EVENTTARGET': 'AspNetPager2', '__EVENTARGUMENT': str(page)}
            yield scrapy.FormRequest(url=response.url, formdata=post_data, callback=self.project,
                                     meta={'page': page, 'company_name': response.meta['company_name'],
                                           'number': response.meta['number']})

    def info(self, response):
        basic_data = Selector(response=response).xpath('//div[@class="news_con"]/table/tr')
        basic_data = basic_data[1:]
        name = basic_data[0].xpath('./td[2]/span/text()').extract_first()
        code = basic_data[0].xpath('./td[4]/span/text()').extract_first()
        unit = basic_data[1].xpath('./td[2]/span/text()').extract_first()
        area = basic_data[1].xpath('./td[4]/span/text()').extract_first()
        docuCode = basic_data[3].xpath('./td[2]/span/text()').extract_first()
        level = basic_data[3].xpath('./td[4]/span/text()').extract_first()
        money = basic_data[4].xpath('./td[2]/span/text()').extract_first()
        acreage = basic_data[4].xpath('./td[4]/span/text()').extract_first()
        trait = basic_data[5].xpath('./td[2]/span/text()').extract_first()
        purpose = basic_data[5].xpath('./td[4]/span/text()').extract_first()
        basic_zz = templates.Project(companyName=response.meta['company_name'], name=name, code=code, unit=unit,
                                     area=area, provinceCode=code,
                                     docuCode=docuCode, level=level, money=money, acreage=acreage, trait=trait,
                                     purpose=purpose
                                     )
        b_data = basic_zz.data()
        print(b_data, '基本信息-------------------')
        yield scrapy.Request(
                             # url='http://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                             url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                             headers={'Content-Type': 'application/json'},
                             callback=self.project_zz,
                             body=json.dumps(b_data),
                             method='POST',
                             meta={'type': '基本信息', 'company_name': response.meta['company_name']}
                             )
        #
        wining_bib_list = Selector(response=response).xpath('//table[@id="GridView1"]')[0].xpath('./tr')
        wining_bib_list = wining_bib_list[1:]
        for w in wining_bib_list:
            bid_url = w.xpath('./td[3]/a/@href').extract_first()
            bid_url = 'http://hngcjs.hnjs.gov.cn' + bid_url
            yield scrapy.Request(url=bid_url, callback=self.win_bid,
                                 meta={'company_name': response.meta['company_name'],
                                       'code': code})

        examination = Selector(response=response).xpath('//table[@id="GridView1"]')[1].xpath('./tr')
        examination = examination[1:]
        for e in examination:
            censorNum = e.xpath('./td[2]/text()').extract_first()
            censorCorpName = e.xpath('./td[3]/text()').extract_first()
            data = templates.MakeDrawing(companyName=response.meta['company_name'], code=code, censorNum=censorNum,
                                         provinceCensorNum=censorNum, censorCorpName=censorCorpName,
                                         # censorEDate=censorEDate
                                         )
            e_data = data.data()
            censorEDate = e.xpath('./td[4]/text()').extract_first()
            time_tuple = (time.strptime(censorEDate, "%Y/%m/%d %H:%M:%S"))
            time1 = time.strftime("%Y-%m-%d", time_tuple)
            e_data['censorEDate'] = time1
            yield scrapy.Request(url='http://api.maotouin.com/rest/companyInfo/addCompanyProjectCensor.htm',
                                 headers={'Content-Type': 'application/json'},
                                 callback=self.project_zz,
                                 body=json.dumps(e_data),
                                 method='POST',
                                 meta={'type': '图纸审查'}
                                 )
            print(data.data(), 'ttttttttttttttttttttttttttttttt', '图纸审查')
        #
        contract = Selector(response=response).xpath('//table[@id="GridView1"]')[2].xpath('./tr')
        contract = contract[1:]
        for c in contract:
            contract_u = c.xpath('./td[2]/a/@href').extract_first()
            recordNum = c.xpath('./td[2]/a/text()').extract_first()
            bid_url = 'http://hngcjs.hnjs.gov.cn' + contract_u
            yield scrapy.Request(url=bid_url, callback=self.contract_info,
                                 meta={'company_name': response.meta['company_name'], 'recordNum': recordNum,
                                       'code': code})

        permit = Selector(response=response).xpath('//table[@id="GridView1"]')[3].xpath('./tr')
        permit = permit[1:]
        for p in permit:
            builderLicenceNum = p.xpath('./td[2]/text()').extract_first()
            consCorpName = p.xpath('./td[3]/text()').extract_first()
            # censorEDate = p.xpath('./td[4]').extract_first()
            p_data = templates.ConstructionPermit(companyName=response.meta['company_name'], code=code,
                                                  builderLicenceNum=builderLicenceNum,
                                                  provinceBuilderLicenceNum=builderLicenceNum,
                                                  consCorpName=consCorpName,
                                                  )
            per_data = p_data.data()
            yield scrapy.Request(
                url='http://api.maotouin.com/rest/companyInfo/addCompanyProjectBuilderLicence.htm',
                headers={'Content-Type': 'application/json'},
                callback=self.project_zz,
                body=json.dumps(per_data),
                method='POST',
                meta={'type': '施工许可'}
            )
            print(p_data.data(), 'ttttttttttttttttttttttttttttttt', '施工许可')

        completed = Selector(response=response).xpath('//table[@id="GV_Cert"]/tr')
        completed = completed[1:]
        for c in completed:
            completed_u = c.xpath('./td[2]/a/@href').extract_first()
            bid_url = 'http://hngcjs.hnjs.gov.cn' + completed_u
            yield scrapy.Request(url=bid_url, callback=self.completed_info,
                                 meta={'company_name': response.meta['company_name'],
                                       'code': code})

    def win_bid(self, response):
        tr = Selector(response=response).xpath('//table[@class="Tab"]/tr')
        agencyCorpName = tr[5].xpath('./td[2]/span/text()').extract_first()
        agencyCorpCode = tr[5].xpath('./td[4]/span/text()').extract_first()
        tenderCorpName = tr[6].xpath('./td[2]/span/text()').extract_first()
        tenderCorpCode = tr[6].xpath('./td[4]/span/text()').extract_first()
        tenderType = tr[7].xpath('./td[2]/span/text()').extract_first()
        tenderClass = tr[7].xpath('./td[4]/span/text()').extract_first()
        tenderResultDate = tr[8].xpath('./td[2]/span/text()').extract_first()
        tenderMoney = tr[8].xpath('./td[4]/span/text()').extract_first()
        prjSize = tr[9].xpath('./td[2]/span/text()').extract_first()
        area = tr[9].xpath('./td[4]/span/text()').extract_first()
        constructorName = tr[10].xpath('./td[2]/text()').extract_first()
        tenderNum = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label3"]/text()').extract_first()
        bid = templates.Mark(companyName=response.meta['company_name'], code=response.meta['code'],
                             tenderNum=tenderNum, provinceTenderNum=tenderNum, agencyCorpName=agencyCorpName,
                             agencyCorpCode=agencyCorpCode, tenderCorpName=tenderCorpName,
                             tenderCorpCode=tenderCorpCode,
                             tenderType=tenderType, tenderClass=tenderClass, tenderResultDate=tenderResultDate,
                             tenderMoney=tenderMoney, area=area, prjSize=prjSize, constructorName=constructorName
                             )
        b_data = bid.data()
        yield scrapy.Request(url='http://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
                             headers={'Content-Type': 'application/json'},
                             callback=self.project_zz,
                             body=json.dumps(b_data),
                             method='POST',
                             meta={'type': '招标信息'}
                             )
        print(bid.data(), '招标信息BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')

    def contract_info(self, response):
        code = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label1"]/text()').extract_first()
        contractNum = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label20"]/text()').extract_first()
        contractType = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label18"]/text()').extract_first()
        proprietorCorpName = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label10"]/text()').extract_first()
        proprietorCorpCode = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label13"]/text()').extract_first()
        contractorCorpCode = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label19"]/text()').extract_first()
        contractorCorpName = Selector(response=response).xpath(
            '//table[@class="Tab"]/tr[7]/td[2]/text()').extract_first()
        createDate = Selector(response=response).xpath('//table[@class="Tab"]/tr[10]/td[2]/text()').extract_first()
        data = templates.Contract(companyName=response.meta['company_name'], code=code, contractNum=contractNum,
                                  contractType=contractType,
                                  recordNum=response.meta['recordNum'],
                                  provinceRecordNum=response.meta['recordNum'],
                                  proprietorCorpName=proprietorCorpName, proprietorCorpCode=proprietorCorpCode,
                                  contractorCorpName=contractorCorpName,
                                  contractorCorpCode=contractorCorpCode, createDate=createDate
                                  )

        data = data.data()
        yield scrapy.Request(url='http://api.maotouin.com/rest/companyInfo/addCompanyProjectContract.htm',
                             headers={'Content-Type': 'application/json'},
                             callback=self.project_zz,
                             body=json.dumps(data),
                             method='POST',
                             meta={'type': '合同信息'}
                             )

        print(response.meta['company_name'], 'cccccccccccccccccccc--合同备案', data)

    def completed_info(self, response):
        code = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label1"]/text()').extract_first()
        prjFinishNum = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label3"]/text()').extract_first()
        factCost = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label18"]/text()').extract_first()
        factArea = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label20"]/text()').extract_first()
        factSize = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label10"]/text()').extract_first()
        prjStructureType = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label13"]/text()').extract_first()
        factBeginDate = Selector(response=response).xpath(
            '//table[@class="Tab"]/tr[7]/td[2]/text()').extract_first()
        factEndDate = Selector(response=response).xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_FormView1_Label19"]/text()').extract_first()
        completed_data = templates.Completion(companyName=response.meta['company_name'], code=code,
                                              prjFinishNum=prjFinishNum,
                                              provincePrjFinishNum=prjFinishNum, factCost=factCost, factArea=factArea,
                                              factSize=factSize, prjStructureType=prjStructureType,
                                              factEndDate=factEndDate,
                                              factBeginDate=factBeginDate
                                              )
        data = completed_data.data()
        yield scrapy.Request(url='http://api.maotouin.com/rest/companyInfo/addCompanyProjectFinish.htm',
                             headers={'Content-Type': 'application/json'},
                             callback=self.project_zz,
                             body=json.dumps(data),
                             method='POST',
                             meta={'type': '竣工验收'}
                             )

        print('JJJJJJJJJJJJJJJJJJJJJJJJ--竣工验收', completed_data.data())

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
