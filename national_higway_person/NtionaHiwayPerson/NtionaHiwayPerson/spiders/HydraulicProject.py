# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import redis
import json
import re


class HydraulicProject(scrapy.Spider):
    name = 'HydraulicProject'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://xypt.mwr.gov.cn/UnitCreInfo/listCydwPage.do?'
        pool = redis.ConnectionPool(
            host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.index = 1
        self.flag = True

    def start_requests(self):
        yield scrapy.Request(url=self.url + 'currentPage=1&showCount=20',
                             callback=self.parse,
                             )

    def parse(self, response):
        # print(response.text)
        if self.flag:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[6].xpath('./a/@onclick') \
                .extract_first()
            self.flag = False
        else:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[8].xpath('./a/@onclick') \
                .extract_first()
        page = re.findall('nextPage\((\d+)\)', page)[0]
        page = int(page) + 1
        print(page, 'page')
        person_url = Selector(response=response).xpath('//table[@id="example-advanced"]/tbody/tr')
        for p in person_url:
            zz = p.xpath('./td[2]/a/@href').extract_first()
            unit_type = p.xpath('./td[3]/text()').extract_first()
            if unit_type is None:
                unit_type = ''
            a = re.findall('javascript:toChangeTop\(\'(.*)\'\);toDetail\(\'(.*)\'\)', zz)
            yield scrapy.Request(url='http://xypt.mwr.gov.cn/UnitCreInfo/frontunitInfoList.do?ID=%s&menu=%s'
                                     % (a[0][1], a[0][0]),
                                 callback=self.company_info,
                                 meta={'unit_type': unit_type}
                                 )
        self.index += 1
        if page != self.index:
            yield scrapy.Request(url=self.url + 'currentPage=%s&showCount=20' % self.index,
                                 callback=self.parse,
                                 )

    def company_zz(self, response):
        print(response.text)

    def company_info(self, response):
        company_name = Selector(response=response).xpath('//td[@colspan="3"]')[0].xpath('./a/@title').extract_first()
        number = Selector(response=response).xpath('//td[@colspan="3"]')[3].xpath(
            'text()').extract_first()
        if number.split():
            number = number.split()[0]
            if len(number) == 18:
                number = number
        else:
            number = ''


        # 项目详情
        project_performance = Selector(response=response).xpath('//div[@id="tab4"]/table/tbody/tr')
        # zz = Selector(response=response)\
        #     .xpath('//div[@id="tab4"]/table/tbody/tr[@id="proj53596ac6358f412198baad26cb24a61b"]')
        # print(zz)

        print(len(project_performance), project_performance.xpath('./td/text()').extract_first(), company_name)
        if len(project_performance) != 1:
            for index, p in enumerate(project_performance):
                project_data = {'project_name': '', 'project_address': '', 'project_status': '', 'project_capital': '',
                                'project_start_date': '', 'project_company': '', 'project_complete': '',
                                'company_name': company_name, 'contract_name': '', 'project_type': '',
                                'project_number': '', 'project_model': '', 'project_place': '',
                                'project_make_status': '', 'project_make_company': '', 'project_make_department': '',
                                'project_engineer_name': '', 'project_engineer_end_time': '',
                                'project_engineer_start_time': '', 'project_technology_name': '',
                                'project_technology_start_time': '', 'project_technology_end_time': '',
                                'project_grade': '', 'contract_capital': '', 'settlement_fund': '',
                                'contract_date': '', 'contract_date_start': '', 'contract_date_end': '',
                                'contract_date_total': '', 'actual_date_start': '', 'actual_date_end': '',
                                'actual_date_total': '', 'project_important': '',
                                'project_important_content': ''
                                }
                easy_info = p.xpath('./td[@align="center"]')
                if len(easy_info) != 0:
                    print(len(easy_info), 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAA', company_name)
                    # 项目名称
                    project_name = easy_info[2].xpath('text()').extract_first()
                    if project_name is not None:
                        project_data['project_name'] = project_name
                    else:
                        continue

                    # 项目地址
                    project_address = easy_info[3].xpath('text()').extract_first()
                    if project_address is not None:
                        project_data['project_address'] = project_address

                    # 项目状态
                    project_status = easy_info[4].xpath('text()').extract_first()
                    if project_status is not None:
                        project_data['project_status'] = project_status

                    # 合同金额(万元)
                    project_capital = easy_info[5].xpath('text()').extract_first()
                    if project_capital is not None:
                        project_data['project_capital'] = project_capital + '万元'

                    # 开工日期
                    project_start_date = easy_info[6].xpath('text()').extract_first()
                    if project_start_date is not None:
                        project_data['project_start_date'] = project_start_date

                    # 建设单位
                    project_company = easy_info[7].xpath('text()').extract_first()
                    if project_company is not None:
                        project_data['project_company'] = project_company

                    # 信息完整度
                    project_complete = easy_info[8].xpath('./font/text()').extract_first()
                    if project_complete is not None:
                            project_data['project_complete'] = project_complete

                    # 项目详细介绍----
                    project_info = Selector(response=response).\
                        xpath('//div[@id="tab4"]/table/tbody/tr')[index+1].xpath('./td/table/tr')

                    contract_name = project_info[1].xpath('./td[2]/text()').extract_first()

                    # 合同名称
                    if company_name is not None:
                        project_data['contract_name'] = contract_name

                    # 项目类型
                    project_type = project_info[2].xpath('./td[2]/text()').extract_first()
                    if project_type is not None:
                        project_data['project_type'] = project_type

                    # 工程编号
                    project_number = project_info[2].xpath('./td[4]/text()').extract_first()
                    if project_number is not None:
                        project_data['project_number'] = project_number

                    # 工程建设模式
                    project_model = project_info[3].xpath('./td[2]/text()').extract_first()
                    if project_model is not None:
                        project_data['project_model'] = project_model

                    # 工程类型
                    engineering_type = project_info[3].xpath('./td[4]/text()').extract_first()
                    if engineering_type is not None:
                        project_data['engineering_type'] = engineering_type

                    # 项目归属
                    project_place = project_info[4].xpath('./td[2]/text()').extract_first()
                    if project_place is not None:
                        project_data['project_place'] = project_place

                    # 工程状态
                    project_make_status = project_info[4].xpath('./td[4]/text()').extract_first()
                    if project_make_status is not None:
                        project_data['project_make_status'] = project_make_status

                    # 建设单位
                    project_make_company = project_info[5].xpath('./td[2]/text()').extract_first()
                    if project_make_company is not None:
                        project_data['project_make_company'] = project_make_company

                    # 项目主管部门
                    project_make_department = project_info[5].xpath('./td[4]/text()').extract_first()
                    if project_make_department is not None:
                        project_data['project_make_department'] = project_make_department

                    # 项目负责人/总监理工程师
                    project_engineer_name = project_info[6].xpath('./td[2]/text()').extract_first()
                    if project_make_department is not None:
                        project_data['project_engineer_name'] = project_engineer_name

                    # 项目负责人/总监理工程师--开始时间
                    project_engineer_time = project_info[6].xpath('./td[3]/text()')
                    if project_make_department is not None:
                        project_engineer_start_time = project_engineer_time[0].extract().split()[0]
                        project_data['project_engineer_start_time'] = project_engineer_start_time
                        project_engineer_end_time = project_engineer_time[1].extract().split()[0]
                        project_data['project_engineer_end_time'] = project_engineer_end_time

                    # 技术负责人/总监理工程师
                    project_engineer_name = project_info[7].xpath('./td[2]/text()').extract_first()
                    if project_make_department is not None:
                        project_data['project_technology_name'] = project_engineer_name

                    # 技术负责人/监理工程师--开始时间
                    project_technology_time = project_info[7].xpath('./td[3]/text()')
                    if project_technology_time is not None:
                        project_technology_start_time = project_technology_time[0].extract().split()[0]
                        project_data['project_technology_start_time'] = project_technology_start_time
                        project_technology_end_time = project_technology_time[1].extract().split()[0]
                        project_data['project_technology_end_time'] = project_technology_end_time

                    # 工程等级
                    project_grade = project_info[8].xpath('./td[2]/text()').extract_first()
                    if project_grade is not None:
                        project_grade = project_grade.split()[0] + project_grade.split()[1] + project_grade.split()[2]
                        project_data['project_grade'] = project_grade

                    # 合同资金
                    contract_capital = project_info[9].xpath('./td[2]/text()').extract_first()
                    if contract_capital is not None:
                        project_data['contract_capital'] = contract_capital + '万元'

                    # 结算金额(万元)
                    settlement_fund = project_info[9].xpath('./td[4]/text()').extract_first()
                    if settlement_fund is not None:
                        project_data['settlement_fund'] = settlement_fund

                    # 合同签订日期
                    contract_date = project_info[10].xpath('./td[2]/text()').extract_first()
                    if contract_date is not None:
                        project_data['contract_date'] = contract_date

                    # 合同期限
                    contract_term = project_info[11].xpath('./td[2]/text()')
                    if contract_date is not None:
                        contract_date_start = contract_term[0].extract().split()[0]
                        contract_date_end = contract_term[1].extract().split()[0]
                        contract_date_total = contract_term[2].extract().split()[0]
                        project_data['contract_date_start'] = contract_date_start
                        project_data['contract_date_end'] = contract_date_end
                        project_data['contract_date_total'] = contract_date_total

                    # 实际工期
                    contract_actual = project_info[12].xpath('./td[2]/text()')
                    if contract_date is not None:
                        actual_date_start = contract_actual[0].extract().split()[0]
                        actual_date_end = contract_actual[1].extract().split()[0]
                        actual_date_total = contract_actual[2].extract().split()[0]
                        project_data['actual_date_start'] = actual_date_start
                        project_data['actual_date_end'] = actual_date_end
                        project_data['actual_date_total'] = actual_date_total

                    # 工程关键指标
                    project_important = project_info[13].xpath('./td[2]/text()').extract_first()
                    if project_important is not None:
                        project_data['project_important'] = project_important

                    # 合同主要内容
                    project_important_content = project_info[14].xpath('./td[2]/text()').extract_first()
                    if project_important is not None:
                        project_data['project_important_content'] = project_important_content

                    print(project_data)


    def ability_zz(self, response):
        print(response)
