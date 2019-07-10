# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import re
import json
from province_project import currency
from province_project import templates


class QingHaiProject(scrapy.Spider):
    name = 'QingHaiProject'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.index = 1
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://jzsc.qhcin.gov.cn/dataservice/query/comp/list'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://jzsc.qhcin.gov.cn'

    def start_requests(self):

        yield scrapy.Request(url=self.url, callback=self.page_transfer)

    def page_transfer(self, response):
        info_page = Selector(response=response).xpath("//a[@sf='pagebar']").extract_first()
        total = 'tt:(\d+),'
        page = 'pc:(\d+),'
        total = re.findall(total, info_page)[0]
        page = re.findall(page, info_page)[0]
        send_data = {'$total': total, '$pgsz': '15', '$reload': '0', '$pg': page}
        yield scrapy.FormRequest(
            url=self.url,
            callback=self.parse,
            formdata=send_data,
            meta={'page': page, 'total': total}
        )

    def parse(self, response):
        div_under_table = Selector(response).xpath('//tbody/tr/@onclick')
        for d in div_under_table:
            company_name = d.extract()
            re_a = 'javascript:location.href=\'(.*)\''
            company_data = re.findall(re_a, company_name)[0]
            # print(company_data, 'aaaaaaaaaaaaaaaaaaaaaaaa')
            yield scrapy.Request(url=self.bigurl + company_data, callback=self.all_project)

        send_data = {'$total': response.meta['total'], '$pgsz': '15', '$reload': '0'}
        # print(response.meta['page'], type(response.meta['page']))
        page = int(response.meta['page'])
        page -= 1
        # self.number -= 1
        if page != 0:
            send_data['$pg'] = str(page)
            yield scrapy.FormRequest(url=self.url, formdata=send_data, callback=self.parse,
                                     meta={'page': page, 'total': response.meta['total']}
                                     )

    def all_project(self, response):
        xx = response.url
        vv = 'http://jzsc.qhcin.gov.cn/dataservice/query/comp/compDetail/(.*)'
        cc = re.findall(vv, xx)[0]
        company_name = Selector(response=response).xpath('//span[@class="user-name"]/text()').extract_first()
        number = Selector(response=response).xpath('//div[@class="bottom"]/dl/dt/text()').extract_first()
        company_name = company_name.split()[0]
        url = 'http://jzsc.qhcin.gov.cn/dataservice/query/comp/compPerformanceListSys/' + cc
        send_data = {'$total': '100',
                     '$pgsz': '100',
                     '$pg': '1',
                     '$reload': '0',
                     }
        yield scrapy.FormRequest(url=url, formdata=send_data, callback=self.project_info,
                                 meta={"company_name": company_name, "number": number}
                                 )

    def project_info(self, response):
        project_url = Selector(response=response).xpath('//a[@target="_blank"]/@href')
        for p in project_url:
            url = re.findall('/dataservice/query/project/projectDetail/(.*)', p.extract())[0]
            xx = 'http://jzsc.qhcin.gov.cn/dataservice/query/project/projectDetail/%s' % url
            print(xx)
            yield scrapy.Request(url=xx, callback=self.project_basic,
                                 meta={'company_name': response.meta['company_name'],
                                       'number': response.meta['number'], 'url': url}
                                 )

    def project_basic(self, response):
        print('标记-------------------------')
        dd_list = Selector(response=response).xpath('//div[@id="project_baseinfo"]/dl/dd')

        code = dd_list[0].xpath('text()').extract_first()

        name = Selector(response=response).xpath('//div[@class="user_info tip"]/@title').extract_first()

        unit = dd_list[2].xpath('text()').extract_first()

        unitLicenseNum = dd_list[3].xpath('text()').extract_first()

        catalog = dd_list[5].xpath('text()').extract_first()

        area = dd_list[6].xpath('text()').extract_first()

        purpose = dd_list[8].xpath('text()').extract_first()

        trait = dd_list[10].xpath('text()').extract_first()

        acreage = dd_list[13].xpath('text()').extract_first()

        acreage = re.findall('(.*)（平方米/米）', acreage)[0]

        docuCode = Selector(response=response).xpath(
            '//div[@id="project_approvalinfo"]/dl/dd[1]/text()').extract_first()

        level = Selector(response=response).xpath('//div[@id="project_approvalinfo"]/dl/dd[2]/text()').extract_first()

        money = Selector(response=response).xpath('//div[@id="project_moneyincome"]/dl/dd[1]/text()').extract_first()
        money = re.findall('(.*) （万元）', money)[0]

        basic_project = currency.Project(companyName=response.meta['company_name'],
                                         code=code, name=name, area=area, unitLicenseNum=unitLicenseNum,
                                         acreage=acreage, docuCode=docuCode, trait=trait, purpose=purpose,
                                         provinceCode=code, level=level, catalog=catalog, unit=unit,
                                         money=money
                                         )
        basic_data = basic_project.data()
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                             headers={'Content-Type': 'application/json'},
                             callback=self.project_zz,
                             body=json.dumps(basic_data),
                             method='POST',
                             meta={'type': '基本信息', 'company_name': basic_data['companyName']}
                             )

        drawing_url = 'http://jzsc.qhcin.gov.cn/dataservice/query/project/projSgtscList/' + response.meta['url']
        yield scrapy.Request(url=drawing_url, callback=self.drawing_list,
                             meta={'companyName': response.meta['company_name'],
                                   'code': code
                                   })

        bid_url = 'http://jzsc.qhcin.gov.cn/dataservice/query/project/projZbtzsList/' + response.meta['url']
        print(bid_url, '招标信息')
        yield scrapy.Request(url=bid_url, callback=self.bid_list,
                             meta={'companyName': response.meta['company_name'],
                                   'code': code
                                   })

        contract_url = 'http://jzsc.qhcin.gov.cn/dataservice/query/project/projHtList/' + \
                       response.meta['url']
        print(contract_url, '合同备案')
        yield scrapy.Request(url=contract_url, callback=self.contract_list,
                             meta={'companyName': response.meta['company_name'],
                                   'code': code
                                   })
        #
        construction_url = 'http://jzsc.qhcin.gov.cn/dataservice/query/project/projSgxkList/' + \
                           response.meta['url']
        print(construction_url, '施工许可')
        yield scrapy.Request(url=contract_url, callback=self.construction_list,
                             meta={'companyName': response.meta['company_name'],
                                   'code': code
                                   })

        completion_url = 'http://jzsc.qhcin.gov.cn/dataservice/query/project/projJgbaList/' + \
                         response.meta['url']
        print(completion_url, '竣工验收')
        yield scrapy.Request(url=contract_url, callback=self.completion_list,
                             meta={'companyName': response.meta['company_name'],
                                   'code': code
                                   })

    def drawing_list(self, response):
        tr = Selector(response=response).xpath('//table[@class="pro_table_box"]/tbody/tr')
        tr = tr[:-1]
        for t in tr:
            censorNum = t.xpath('./td[3]/text()').extract_first()
            censorCorpName = t.xpath('./td[4]/text()').extract_first()
            drawing_data = templates.MakeDrawing(companyName=response.meta['companyName'], code=response.meta['code'],
                                                 censorNum=censorNum, provinceCensorNum=censorNum,
                                                 censorCorpName=censorCorpName
                                                 )
            print(drawing_data.data(), '*****************8', '施工图纸审查', response.url)
            drawing_data = drawing_data.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectCensor.htm',
                                 headers={'Content-Type': 'application/json'},
                                 callback=self.project_zz,
                                 body=json.dumps(drawing_data),
                                 meta={'type': '施工图纸审查'},
                                 method='POST'
                                 )

    def bid_list(self, response):
        tr = Selector(response=response).xpath('//table[@class="pro_table_box"]/tbody/tr')
        tr = tr[:-1]
        for t in tr:
            tenderClass = t.xpath('./td[3]/text()').extract_first()
            tenderType = t.xpath('./td[4]/text()').extract_first()
            tenderNum = t.xpath('./td[5]/text()').extract_first()
            tenderResultDate = t.xpath('./td[6]/text()').extract_first()
            tenderResultDate = tenderResultDate.replace('年', '-')
            tenderResultDate = tenderResultDate.replace('月', '-')
            tenderResultDate = tenderResultDate.replace('日', '')
            bid_data = templates.Mark(companyName=response.meta['companyName'], code=response.meta['code'],
                                      tenderClass=tenderClass, tenderType=tenderType,
                                      tenderNum=tenderNum, provinceTenderNum=tenderNum,
                                      tenderResultDate=tenderResultDate
                                      )
            print(bid_data.data(), '*****************8', '招标信息', response.url)
            bid_data = bid_data.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
                                 headers={'Content-Type': 'application/json'},
                                 callback=self.project_zz,
                                 body=json.dumps(bid_data),
                                 meta={"type": '招标'},
                                 method='POST'
                                 )

    def contract_list(self, response):
        tr = Selector(response=response).xpath('//table[@class="pro_table_box"]/tbody/tr')
        tr = tr[:-1]
        for t in tr:
            recordNum = t.xpath('./td[2]/text()').extract_first()
            contractType = t.xpath('./td[3]/text()').extract_first()
            contractDate = t.xpath('./td[4]/text()').extract_first()
            contractMoney = t.xpath('./td[5]/text()').extract_first()
            contractorCorpName = t.xpath('./td[6]/text()').extract_first()
            contract_data = templates.Contract(companyName=response.meta['companyName'], code=response.meta['code'],
                                               recordNum=recordNum, provinceRecordNum=recordNum,
                                               contractType=contractType, contractDate=contractDate,
                                               contractMoney=contractMoney, contractorCorpName=contractorCorpName
                                               )
            print(contract_data.data(), '*****************8', '合同备案信息', response.url)
            contract_data = contract_data.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectContract.htm',
                                 headers={'Content-Type': 'application/json'},
                                 callback=self.project_zz,
                                 body=json.dumps(contract_data),
                                 meta={"type": '合同备案'},
                                 method='POST'
                                 )

    def construction_list(self, response):
        tr = Selector(response=response).xpath('//table[@class="pro_table_box"]/tbody/tr')
        tr = tr[:-1]
        for t in tr:
            builderLicenceNum = t.xpath('./td[3]/text()').extract_first()
            createDate = t.xpath('./td[5]/text()').extract_first()
            construction_data = templates.ConstructionPermit(companyName=response.meta['companyName'],
                                                             code=response.meta['code'],
                                                             builderLicenceNum=builderLicenceNum,
                                                             provinceBuilderLicenceNum=builderLicenceNum,
                                                             createDate=createDate
                                                             )
            print(construction_data.data(), '*****************8', '施工许可', response.url)
            construction_data = construction_data.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectBuilderLicence.htm',
                                 headers={'Content-Type': 'application/json'},
                                 callback=self.project_zz,
                                 body=json.dumps(construction_data),
                                 meta={"type": '施工许可'},
                                 method='POST'
                                 )

    def completion_list(self, response):
        tr = Selector(response=response).xpath('//table[@class="pro_table_box"]/tbody/tr')
        tr = tr[:-1]
        for t in tr:
            prjFinishNum = t.xpath('./td[3]/text()').extract_first()
            completion_data = templates.Completion(companyName=response.meta['companyName'],
                                                   code=response.meta['code'],
                                                   prjFinishNum=prjFinishNum,
                                                   provincePrjFinishNum=prjFinishNum,
                                                   )
            print(completion_data.data(), '*****************8', '竣工验收', response.url)
            completion_data = completion_data.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectFinish.htm',
                                 headers={'Content-Type': 'application/json'},
                                 callback=self.project_zz,
                                 body=json.dumps(completion_data),
                                 meta={"type": '竣工验收'},
                                 method='POST'
                                 )

    def project_zz(self, response):
        not_company_code = json.loads(response.text)['code']
        if not_company_code == -102 and response.meta['type'] == '基本信息':
            not_search_company_name = response.meta['company_name']
            self.r.sadd('title_name1', not_search_company_name)
            print('正在添加公司基本信息', not_search_company_name)
        else:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>%s------%s' % (response.text, response.meta['type'],))