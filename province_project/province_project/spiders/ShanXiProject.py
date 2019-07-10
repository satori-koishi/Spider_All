# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
from scrapy.http import Request
import time
import re
import json
from province_project import templates


class ShanXiProject(scrapy.Spider):
    name = 'ShanXiProject'
    start_urls = [
        'http://jzscyth.shaanxi.gov.cn:7001/PDR/network/informationSearch/informationSearchList?libraryName'
        '=enterpriseLibrary&pid1=610000']

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.flag = True
        self.index = 1
        self.data = {'licenseNum': '', 'contactMan': '', 'area': '', 'companyArea': '陕西省', 'contactAddress': '',
                     'contactPhone': '', 'token': self.token}

    def parse(self, response):
        my_tr = Selector(response).xpath('//table[@id="enterpriseLibraryIsHides"]/tr/td[2]/p/a/@onclick')
        for m in my_tr:
            u = m.extract()
            s = 'vie1\(\'(.*)\',\'(.*)\' ,\'(.*)\',\'\'\)'
            list_z = re.findall(s, u)
            company_url = 'http://jzscyth.shaanxi.gov.cn:7001/PDR/network/Enterprise/Informations/view?enid=%s&name' \
                          '=%s&org_code=%s&type=' % (
                              list_z[0][1], list_z[0][0], list_z[0][2])
            yield Request(url=company_url, callback=self.company_information, dont_filter=True)
        if self.flag:
            page = Selector(response=response).xpath('//td[@class="page1"]/text()').extract_first()
            xx = '共(\d+)页'
            page = re.findall(xx, page)[0]
            self.flag = False
        else:
            page = int(response.meta['page'])
        self.index = self.index + 1
        if self.index != int(page):
            url = 'http://jzscyth.shaanxi.gov.cn:7001/PDR/network/informationSearch/informationSearchList?' \
                  'pid1=610000&pageNumber=%s&libraryName=enterpriseLibrary' % self.index
            yield Request(url=url, callback=self.parse, dont_filter=True, meta={'page': page})

    def company_information(self, response):
        company_name = Selector(response=response).xpath('//td[@colspan="3"]/text()').extract_first()
        number = Selector(response=response).xpath('//table[@class="detailTable"]')[0] \
            .xpath('./tr[2]/td[4]/text()').extract_first()
        company_name = company_name.split()[0]
        # repeat = self.r.sadd('Company_name', company_name)
        repeat = 1
        if repeat != 0:
            if number.split():
                number = number[0]
                if len(number) == 18:
                    number = number
            else:
                number = ''

            project_info = Selector(response=response).xpath('//table[@class="detailTable"]')[4].xpath('./tr')
            title = project_info[0].xpath('./td/text()').extract()[0]
            if title == '项目信息（0个）':
                print('没有项目的公司--%s' % company_name)
            else:
                print('当前公司%s----项目%s' % (company_name, title))
                # print(len(project_info))
                project_info = project_info[2:]
                print(len(project_info), 'BBBBBBBBBBBBBBBBBB')
                for p in project_info:
                    project_url = p.xpath('./td[2]/p/a/@onclick').extract_first()
                    xx = 'window.open\(\'/(.*)\', \'dasfddd.*|window.open\(\'/(.*)\', \'fdsafa.*'
                    cc = re.findall(xx, project_url)[0]
                    if cc[0]:
                        url = cc[0]
                    else:
                        url = cc[1]
                    yield scrapy.Request(url='http://jzscyth.shaanxi.gov.cn:7001/' + url,
                                         callback=self.company_project,
                                         meta={'company_name': company_name, 'number': number},
                                         dont_filter=True
                                         )
        else:
            print('此公司信息已经存在', company_name)

    def company_project(self, response):
        basic = Selector(response=response).xpath('//table[@class="detailTable"]')[0]
        basic_tr = basic.xpath('./tr')
        project_name = basic_tr[1].xpath('./td')[3].xpath('text()').extract_first()
        project_number = basic_tr[1].xpath('./td')[1].xpath('text()').extract_first()
        area = basic_tr[3].xpath('./td')[3].xpath('text()').extract_first()
        if area is not None:
            area_data = ''
            for a in area.split():
                area_data += a
        else:
            area_data = ''
        unit = basic_tr[2].xpath('./td')[3].xpath('text()').extract_first()

        unitLicenseNum = basic_tr[3].xpath('./td')[1].xpath('text()').extract_first()

        catalog = basic_tr[2].xpath('./td')[1].xpath('text()').extract_first()

        traits = basic_tr[7].xpath('./td')[3].xpath('text()').extract_first()

        purpose = basic_tr[8].xpath('./td')[1].xpath('text()').extract_first()

        money = basic_tr[6].xpath('./td')[1].xpath('text()').extract_first()

        acreage = basic_tr[6].xpath('./td')[3].xpath('text()').extract_first()

        level = basic_tr[4].xpath('./td')[3].xpath('text()').extract_first()

        docuCode = basic_tr[4].xpath('./td')[1].xpath('text()').extract_first()

        ccc = templates.Project(name=project_name, companyName=response.meta['company_name'],
                               area=area_data, provinceCode=project_number, unit=unit, unitLicenseNum=unitLicenseNum,
                               catalog=catalog, trait=traits, purpose=purpose, money=money, acreage=acreage,
                               level=level,
                               docuCode=docuCode, code=project_number
                               )
        basic_data = ccc.data()
        print('基本信息', basic_data)
        yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProject.htm',
                             headers={'Content-Type': 'application/json'},
                             method='POST',
                             body=json.dumps(basic_data),
                             callback=self.project_zz,
                             meta={'type': '基本信息', 'company_name': basic_data['companyName']}
                             )
        # print(data)

        mark = Selector(response=response).xpath('//table[@class="detailTable"]')[1]
        mark_tr = mark.xpath('./tr')
        del mark_tr[0]
        mark_list = [k for index, k in enumerate(mark_tr) if (index % 2 != 0)]
        print(len(mark_list), 'mmmmmmmmmmmmmmmmmmmm')
        for m in mark_list:
            td = m.xpath('./td')
            if len(td) == 1:
                pass
                # print(len(td), '没有招标信息的', project_name)
            else:
                project_code = td[0].xpath('./a/text()').extract_first()

                build_size = td[1].xpath('text()').extract_first()

                mark_name = td[2].xpath('text()').extract_first()

                have_project = td[3].xpath('text()').extract_first()

                mark_data = templates.Mark(companyName=response.meta['company_name'],
                                          tenderNum=project_code,
                                          prjSize=build_size,
                                          provinceTenderNum=project_code,
                                          agencyCorpName=mark_name,
                                          tenderCorpName=have_project,
                                          code=project_number)
                make_zz_data = mark_data.data()
                print(project_code, build_size, mark_name, have_project, '招标信息')
                yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectTender.htm',
                                     method='POST',
                                     headers={'Content-Type': 'application/json'},
                                     body=json.dumps(make_zz_data),
                                     callback=self.project_zz,
                                     meta={'type': '招标信息'}
                                     )

        contract = Selector(response=response).xpath('//table[@class="detailTable"]')[2]
        contract = contract.xpath('./tr')
        del contract[0]
        contract_list = [k for index, k in enumerate(contract) if (index % 2 != 0)]
        for m in contract_list:
            td = m.xpath('./td')
            if len(td) == 1:
                print(len(td), '没有合同信息的', project_name)
            else:
                contract_mark_number = td[0].xpath('text()').extract_first()

                contract_number = td[1].xpath('text()').extract_first()

                send_company = td[2].xpath('text()').extract_first()

                make_company = td[3].xpath('text()').extract_first()

                union_company = td[4].xpath('text()').extract_first()

                contract_object = templates.Contract(companyName=response.meta['company_name'],
                                                    code=project_number,
                                                    recordNum=contract_mark_number, contractNum=contract_number,
                                                    proprietorCorpName=send_company, contractorCorpName=make_company,
                                                    unionCorpName=union_company, provinceRecordNum=contract_mark_number
                                                    )
                contract_data = contract_object.data()
                print('合同信息', contract_data)
                yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectContract'
                                         '.htm',
                                     method='POST',
                                     headers={'Content-Type': 'application/json'},
                                     body=json.dumps(contract_data),
                                     callback=self.project_zz,
                                     meta={'type': '合同信息'}
                                     )

        make_drawing = Selector(response=response).xpath('//table[@class="detailTable"]')[3]
        make_drawing = make_drawing.xpath('./tr')

        make_see_number = make_drawing[1].xpath('./td')[1].xpath('text()').extract_first()

        make_see_name = make_drawing[1].xpath('./td')[3].xpath('text()').extract_first()

        drawing_num = make_drawing[2].xpath('./td')[1].xpath('text()').extract_first()

        see_date = make_drawing[2].xpath('./td')[3].xpath('text()').extract_first()

        see_name = make_drawing[3].xpath('./td')[1].xpath('text()').extract_first()

        see_num = make_drawing[3].xpath('./td')[3].xpath('text()').extract_first()

        desgin_name = make_drawing[4].xpath('./td')[1].xpath('text()').extract_first()

        desgin_num = make_drawing[4].xpath('./td')[3].xpath('text()').extract_first()

        make_size = make_drawing[5].xpath('./td')[1].xpath('text()').extract_first()

        ok_pass = make_drawing[5].xpath('./td')[3].xpath('text()').extract_first()

        see_error = make_drawing[6].xpath('./td')[1].xpath('text()').extract_first()

        see_number = make_drawing[6].xpath('./td')[3].xpath('text()').extract_first()

        drawing = templates.MakeDrawing(
            censorNum=make_see_number,
            censorCorpName=make_see_name,
            censorCorpCode=drawing_num,
            censorEDate=see_date,
            surveyCorpName=see_name,
            surveyCorpCode=see_num,
            designCorpName=desgin_name,
            designCorpCode=desgin_num,
            companyName=response.meta['company_name'],
            code=project_number,
            prjSize=make_size,
            engineers=[],
            provinceCensorNum=make_see_number
        )

        drawing_data = drawing.data()
        if drawing_data['censorNum']:
            print(drawing_data, '施工图纸信息')
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectCensor.htm',
                                 headers={'Content-Type': 'application/json'},
                                 method='POST',
                                 body=json.dumps(drawing_data),
                                 callback=self.project_zz,
                                 meta={'type': '施工图纸信息'}
                                 )

        construction = Selector(response=response).xpath('//table[@class="detailTable"]')[5]
        construction_tr = construction.xpath('./tr')

        # 施工许可证系统备案编号
        construction_num = construction_tr[1].xpath('./td')[1].xpath('text()').extract_first()

        # 暂时用不到
        usr_plan_land_num = construction_tr[1].xpath('./td')[3].xpath('text()').extract_first()

        # 暂时用不到
        usr_make_land_num = construction_tr[2].xpath('./td')[1].xpath('text()').extract_first()

        # 施工图审查合格书编号
        qualified_num = construction_tr[2].xpath('./td')[3].xpath('text()').extract_first()

        # 合同金额(万元)
        money_capital = construction_tr[3].xpath('./td')[1].xpath('text()').extract_first()

        # 面积（平方米）
        construction_area = construction_tr[3].xpath('./td')[3].xpath('text()').extract_first()

        # 建设规模暂时用不到
        construction_size = construction_tr[4].xpath('./td')[1].xpath('text()').extract_first()

        # 发证日期
        construction_date = construction_tr[4].xpath('./td')[3].xpath('text()').extract_first()

        # 勘察单位名称
        c_survey_name = construction_tr[5].xpath('./td')[1].xpath('text()').extract_first()

        # 勘察单位组织机构代码
        c_survey_num = construction_tr[5].xpath('./td')[3].xpath('text()').extract_first()

        # 设计单位名称
        c_degsin_name = construction_tr[6].xpath('./td')[1].xpath('text()').extract_first()

        # 设计单位组织机构代码
        c_degsin_num = construction_tr[6].xpath('./td')[3].xpath('text()').extract_first()

        # 施工单位名称
        c_make_name = construction_tr[7].xpath('./td')[1].xpath('text()').extract_first()

        # 施工单位组织机构代码
        c_make_num = construction_tr[7].xpath('./td')[3].xpath('text()').extract_first()

        # 施工单位安全生产许可证编号
        c_make_safe_num = construction_tr[8].xpath('./td')[1].xpath('text()').extract_first()

        # 监理单位名称
        c_supervisor_name = construction_tr[8].xpath('./td')[3].xpath('text()').extract_first()

        # 监理单位组织机构代码
        c_supervisor_num = construction_tr[9].xpath('./td')[1].xpath('text()').extract_first()

        # 项目经理姓名
        c_project_person_name = construction_tr[9].xpath('./td')[3].xpath('text()').extract_first()

        # 施工图审查人员证件类型
        c_name_person_idctype = construction_tr[10].xpath('./td')[1].xpath('text()').extract_first()

        # 项目经理身份证
        c_name_person_idcard = construction_tr[10].xpath('./td')[3].xpath('text()').extract_first()

        # 总监理工程师姓名
        c_chief_name = construction_tr[11].xpath('./td')[1].xpath('text()').extract_first()

        # 总监理工程师证件类型
        c_chief_idtype = construction_tr[11].xpath('./td')[3].xpath('text()').extract_first()

        # 总监理工程师证件号码
        c_chief_idcard = construction_tr[12].xpath('./td')[1].xpath('text()').extract_first()

        # 安全生产管理人员姓名
        c_safe_manager = construction_tr[12].xpath('./td')[3].xpath('text()').extract_first()

        # 安全生产管理证件类型
        c_safe_idtype = construction_tr[13].xpath('./td')[1].xpath('text()').extract_first()

        # 安全生产管理人员姓名
        c_safe_idcard = construction_tr[13].xpath('./td')[3].xpath('text()').extract_first()

        # 安全生产考核合格证书编号
        c_safe_assessenment_num = construction_tr[14].xpath('./td')[1].xpath('text()').extract_first()

        # 安全生产管理人员类型
        c_safe_assessenment_type = construction_tr[14].xpath('./td')[3].xpath('text()').extract_first()

        construction_model = templates.ConstructionPermit(builderLicenceNum=construction_num, censorNum=qualified_num,
                                                         contractMoney=money_capital, area=construction_area,
                                                         econCorpName=c_survey_name, econCorpCode=c_survey_num,
                                                         designCorpName=c_degsin_name, designCorpCode=c_degsin_num,
                                                         consCorpName=c_make_name, consCorpCode=c_make_num,
                                                         superCorpName=c_supervisor_name,
                                                         superCorpCode=c_supervisor_num,
                                                         constructorName=c_project_person_name,
                                                         constructorIDCard=c_name_person_idcard,
                                                         supervisionName=c_chief_name,
                                                         supervisionIDCard=c_chief_idcard,
                                                         companyName=response.meta['company_name'],
                                                         code=project_number,
                                                         provinceBuilderLicenceNum=construction_num
                                                         )
        construction_make_data = construction_model.data()
        print('施工许可信息', construction_make_data)
        if construction_make_data['builderLicenceNum']:
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo'
                                     '/addCompanyProjectBuilderLicence.htm',
                                 headers={'Content-Type': 'application/json'},
                                 method='POST',
                                 body=json.dumps(construction_make_data),
                                 callback=self.project_zz,
                                 meta={'type': '施工许可信息'}
                                 )

        completion_info = Selector(response=response).xpath('//table[@class="detailTable"]')[8]
        completion_tr = completion_info.xpath('./tr')
        # 竣工备案编号
        completion_num = completion_tr[1].xpath('./td')[1].xpath('text()').extract_first()

        # 施工许可证编号
        completion_make_numer = completion_tr[1].xpath('./td')[3].xpath('text()').extract_first()

        # 质量检测机构名称
        test_name = completion_tr[2].xpath('./td')[1].xpath('text()').extract_first()

        # 质量检测机构组织机构代码
        test_number = completion_tr[2].xpath('./td')[3].xpath('text()').extract_first()

        # 实际造价（万元）
        actual_capital = completion_tr[3].xpath('./td')[1].xpath('text()').extract_first()

        # 实际面积（平方米）
        actual_area = completion_tr[3].xpath('./td')[3].xpath('text()').extract_first()

        # 实际建设规模
        actual_size = completion_tr[4].xpath('./td')[1].xpath('text()').extract_first()

        # 结构体系
        c_body = completion_tr[4].xpath('./td')[3].xpath('text()').extract_first()

        # 备注
        remarks = completion_tr[5].xpath('./td')[1].xpath('text()').extract_first()

        Completion_data = templates.Completion(
            companyName=response.meta['company_name'], code=project_number, prjFinishNum=completion_num,
            factCost=actual_capital, factArea=actual_area, factSize=actual_size, prjStructureType=c_body,
            mark=remarks, provincePrjFinishNum=completion_num
        )
        Completion_zz = Completion_data.data()
        if Completion_zz['prjFinishNum']:
            print('当前公司----%s---%s--竣工数据' % (project_name, Completion_zz))
            yield scrapy.Request(url='https://api.maotouin.com/rest/companyInfo/addCompanyProjectFinish.htm',
                                 headers={'Content-Type': 'application/json'},
                                 method='POST',
                                 body=json.dumps(Completion_zz),
                                 callback=self.project_zz,
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
        if not_company_code == -102 or not_company_code == -118:
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
