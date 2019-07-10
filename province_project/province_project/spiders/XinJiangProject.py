# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import re
import json
from province_project import templates


class XinJiangProject(scrapy.Spider):
    name = 'XinJiangProject'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.index = 1
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.url = 'http://jsy.xjjs.gov.cn/dataservice/query/comp/list'
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.bigurl = 'http://jsy.xjjs.gov.cn'

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
            yield scrapy.Request(url=self.bigurl + company_data, callback=self.all_project)

        send_data = {'$total': response.meta['total'], '$pgsz': '15', '$reload': '0'}
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
        vv = 'http://jsy.xjjs.gov.cn/dataservice/query/comp/compDetail/(.*)'
        cc = re.findall(vv, xx)[0]
        company_name = Selector(response=response).xpath('//span[@class="user-name"]/text()').extract_first()
        number = Selector(response=response).xpath('//div[@class="bottom"]/dl/dt/text()').extract_first()
        company_name = company_name.split()[0]
        url = 'http://jsy.xjjs.gov.cn/dataservice/query/comp/compPerformanceListSys/' + cc
        send_data = {'$total': '100',
                     '$pgsz': '100',
                     '$pg': '1',
                     '$reload': '0',
                     }
        yield scrapy.FormRequest(url=url, formdata=send_data, callback=self.project_info,
                                 meta={"company_name": company_name, "number": number}
                                 )

    def project_info(self, response):
        # project_name = Selector(response=response).xpath('//a[@target="_blank"]/text()')
        project_url = Selector(response=response).xpath('//a[@target="_blank"]/@href')
        print(len(project_url), 'AAAAAAAAAAAAAAAAAAAAAAAAA')
        project_xx = {'$total': '100',
                      '$pgsz': '100',
                      '$pg': '1',
                      '$reload': '0'}
        u = 'http://jsy.xjjs.gov.cn/dataservice/query/project/projectDetail/'
        for p in project_url:
            print(p.extract(), 'KKKKKKKKKKKKKK')
            url = re.findall('/dataservice/query/project/projectDetail/(.*)', p.extract())[0]
            print(url, 'LLLLLLLLLLLLLLLLL')
            xx = 'http://jsy.xjjs.gov.cn/dataservice/query/project/projPackList/%s/1' % url
            u = 'http://jsy.xjjs.gov.cn/dataservice/query/project/projectDetail/' + url
            yield scrapy.Request(url=u, callback=self.basic_project,
                                 meta={'company_name': response.meta['company_name'],
                                       'number': response.meta['number']})
            yield scrapy.FormRequest(url=xx, formdata=project_xx, callback=self.detailed_info,
                                     meta={'company_name': response.meta['company_name']}
                                     )

    def basic_project(self, response):
        dd = Selector(response=response).xpath('//div[@id="project_baseinfo"]/dl/dd')
        name = Selector(response=response).xpath('//span[@class="user-name"]/text()').extract_first()
        code = dd[0].xpath('text()').extract_first()
        unit = dd[2].xpath('text()').extract_first()
        unitLicenseNum = dd[3].xpath('text()').extract_first()
        catalog = dd[5].xpath('text()').extract_first()
        area = dd[6].xpath('text()').extract_first()
        purpose = dd[8].xpath('text()').extract_first()
        trait = dd[10].xpath('text()').extract_first()
        acreage = dd[13].xpath('text()').extract_first()
        docuCode = Selector(response=response).xpath(
            '//div[@id="project_approvalinfo"]/dl/dd[1]/text()').extract_first()
        level = Selector(response=response).xpath('//div[@id="project_approvalinfo"]/dl/dd[2]/text()').extract_first()
        money = Selector(response=response).xpath('//div[@id="project_moneyincome"]/dl/dd[1]/text()').extract_first()
        money = re.findall('(.*) （万元）', money)[0]
        acreage = re.findall('(.*)（平方米/米）', acreage)[0]
        basic = templates.Project(companyName=response.meta['company_name'], code=code, name=name,
                                  provinceCode=code, unit=unit, unitLicenseNum=unitLicenseNum,
                                  catalog=catalog, area=area, purpose=purpose, trait=trait,
                                  docuCode=docuCode, level=level, acreage=acreage, money=money
                                  )
        basic_data = basic.data()
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                             headers={'Content-Type': 'application/json'},
                             callback=self.project_zz,
                             body=json.dumps(basic_data),
                             method='POST',
                             meta={'type': '基本信息', 'company_name': basic_data['companyName']}
                             )

    def detailed_info(self, response):
        url_project = Selector(response=response).xpath('//a[@target="_blank"]/@href')
        for u in url_project:
            xx = 'http://jsy.xjjs.gov.cn' + u.extract()
            yield scrapy.Request(url=xx, callback=self.info,
                                 meta={'company_name': response.meta['company_name']})

    def info(self, response):

        number_code = re.findall('http://jsy.xjjs.gov.cn/dataservice/query/bd/toBdDetail/(.*)', response.url)[0]
        tenderMoney = Selector(response=response).xpath('//div[@id="project_zb"]/dl//dd[6]/text()').extract_first()
        code = Selector(response=response).xpath('//div[@id="project_baseinfo"]/dl//dd[1]/text()').extract_first()
        other_info = {
            '$total': '100',
            '$pgsz': '100',
            '$pg': '1',
            '$reload': '$reload'
        }

        yield scrapy.FormRequest(url='http://jsy.xjjs.gov.cn/dataservice/query/bd/toGczbProj/' + number_code,
                                 formdata=other_info, callback=self.tendering_info,
                                 meta={'company_name': response.meta['company_name'],
                                       'code': code,
                                       'tenderMoney': tenderMoney
                                       }
                                 )

        yield scrapy.FormRequest(url='http://jsy.xjjs.gov.cn/dataservice/query/bd/toSgxkProj/' + number_code,
                                 formdata=other_info, callback=self.construction_info,
                                 meta={'company_name': response.meta['company_name'],
                                       'code': code}
                                 )

        # yield scrapy.FormRequest(url='http://jsy.xjjs.gov.cn/dataservice/query/bd/toJgbaProj/' + number_code,
        #                          formdata=other_info, callback=self.completed_info,
        #                          meta={'company_name': response.meta['company_name'],
        #                                'number': response.meta['number']}
        #                          )

    def tendering_info(self, response):
        tr = Selector(response=response).xpath('//tr[@class="row"]')
        print('招标信息', '---------', response.meta['company_name'])
        for t in tr:
            td = t.xpath('./td')
            tendering_type = td[2].xpath('text()').extract_first()
            tendering_method = td[3].xpath('text()').extract_first()
            wining_bidder = td[4].xpath('text()').extract_first()
            wining_number = td[5].xpath('text()').extract_first()
            wining_data = td[6].xpath('text()').extract_first()
            tendering = templates.Mark(companyName=response.meta['company_name'],
                                       code=response.meta['code'],
                                       tenderClass=tendering_type,
                                       tenderType=tendering_method,
                                       tenderNum=wining_number,
                                       provinceTenderNum=wining_number,
                                       tenderResultDate=wining_data,
                                       tenderCorpName=wining_bidder,
                                       tenderMoney=response.meta['tenderMoney'],
                                       )
            t_data = tendering.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
                                 headers={'Content-Type': 'application/json'},
                                 method='POST',
                                 body=json.dumps(t_data),
                                 callback=self.project_zz,
                                 meta={'type': '招标'}
                                 )
            print('招标信息', t_data, '---------', response.meta['company_name'])

    # def contract_info(self, response):
    #     tr = Selector(response=response).xpath('//tr[@class="row"]')
    #     print('合同信息', len(tr), response.meta['company_name'], tr)

    def construction_info(self, response):
        tr = Selector(response=response).xpath('//tr[@class="row"]')
        for t in tr:
            td = t.xpath('./td')
            builderLicenceNum = td[2].xpath('text()').extract_first()
            createDate = td[4].xpath('text()').extract_first()
            construct = templates.ConstructionPermit(companyName=response.meta['company_name'],
                                                     code=response.meta['code'],
                                                     builderLicenceNum=builderLicenceNum,
                                                     provinceBuilderLicenceNum=builderLicenceNum,
                                                     createDate=createDate
                                                     )
            cons_data = construct.data()
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
                                 headers={'Content-Type': 'application/json'},
                                 method='POST',
                                 body=json.dumps(cons_data),
                                 callback=self.project_zz,
                                 meta={'type': '施工许可'}
                                 )

    def completed_info(self, response):
        tr = Selector(response=response).xpath('//tr[@class="row"]')
        print('工程竣工信息', len(tr), response.meta['company_name'], tr)

    def project_zz(self, response):
        not_company_code = json.loads(response.text)['code']
        if not_company_code == -102 and response.meta['type'] == '基本信息':
            not_search_company_name = response.meta['company_name']
            self.r.sadd('title_name1', not_search_company_name)
            print('正在添加公司基本信息', not_search_company_name)
        else:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>%s------%s' % (response.text, response.meta['type'],))
