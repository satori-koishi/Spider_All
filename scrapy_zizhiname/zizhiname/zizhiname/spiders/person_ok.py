# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
from scrapy.http import Request
import json
import redis
from .. import items
import datetime
import time
import logging


class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    name = 'person_ok'

    def start_requests(self):
        """爬虫起始"""
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        # 本公司接口
        self.tongnie = 'https://api.maotouin.com/rest/companyInfo/addCompanyEngineer.htm'
        # 起始url
        self.big_url = 'http://jzsc.mohurd.gov.cn'
        # form表单url
        self.url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
        # r = redis.StrictRedis(host='106.12.112.205 ', port='6379', decode_responses=True, password='tongna888')
        pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        redis_len = self.r.scard('person')

        logging.error('当前数据长度%s' % redis_len + '\n\n')
        while redis_len != 0:
            name = self.r.spop("person").decode('utf8')
            yield scrapy.FormRequest(self.url,
                                     formdata={'qy_name': name},
                                     callback=self.parse, meta={'company_name': name})
            data_time = datetime.datetime.now()
            data_time = str(data_time)
            AAA = data_time + '公司添加访问成功%s' % name
            logging.error(AAA + '\n\n')

    def parse(self, response):
        # 进入当前公司
        """选择公司"""
        corporate_url = Selector(response=response).xpath('//td[@class="text-left primary"]/a/@href').extract_first()
        if corporate_url is not None:
            url = self.big_url + corporate_url
            print('已经查找到此公司' + '\n\n')
            return Request(url=url, callback=self.detailed_information)
        # self.r.scard(response.meta['company_name'], 'not_search_company')
        company_error = '对不起，未查询到此公司的信息-----' + response.meta['company_name']
        self.r.sadd('situyi_person_not_search', response.meta['company_name'])
        # logging.info(company_error)
        print(company_error)

    # 拿到公司人员ajxs的数据
    def detailed_information(self, response):
        """人员基本信息表"""
        url = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li[2]/a/@data-url').extract_first()
        url = self.big_url + url
        # logging.info('正在访问' + '人员信息表\n\n')
        print('正在访问' + '人员信息表\n\n')
        return Request(url=url, callback=self.person, )

    # 拿到每个人员的url地址
    def person(self, response):
        """当前公司所有人员url"""
        # 获取当前表里的所有数据
        mycontinue = True
        tr = Selector(response=response).xpath('//tbody/tr')
        # 获取当前有多少数据
        all_date = Selector(response=response).xpath(
            '//div[@class="comp_regstaff_links"]/a[1]/span/text()').extract_first()
        # 去除不需要的
        one_name = Selector(response=response).xpath('//tbody/tr[1]/td[2]/a/text()').extract_first()
        all_date = all_date.replace('）', '')
        all_date = int(all_date.replace('（', ''))
        if all_date == 0:
            print('----公司无人员\n\n')
            return 'zz'
        if all_date < 26:
            # logging.info( '------人员无分页\n\n')
            logging.error('------人员无分页\n\n')
            mycontinue = False
        # 算出有能有多少页
        self.page = all_date // 25 + 2
        # 拿出所有的人员的A标签属性
        for r in tr:
            one_person = r.xpath('./td/a/@onclick').extract_first()
            if not one_person == None:
                person_url = one_person.split('top.window.location.href=\'')[1]
                person_url = person_url.split('\'')[0]
                person_url = self.big_url + person_url
                time.sleep(0.5)
                yield Request(url=person_url, callback=self.person_detailed)

            # 查看是否有分页
        another_page = Selector(response=response).xpath('//div[@class="clearfix"]')
        # 如果不够分页或者，没有分页选择器这不执行
        if not another_page == [] and mycontinue:
            for a in range(2, self.page):
                print(a)
                a = str(a)
                yield scrapy.FormRequest(response.url, formdata={'$pg': a}, callback=self.person)
            # 只循环一次
            mycontinue = False

    # 获取执业注册信息

    def person_detailed(self, response):
        """人员证件详细表"""

        # 需要发送的人员证件信息
        person_document = {}
        # person_document['companyName '] = self.corporate_name
        # 人员名称
        person_name = Selector(response=response).xpath('//div[@class="user_info spmtop"]/b/text()').extract_first()
        person_document['name'] = person_name

        # 人员性别
        person_sex = Selector(response=response).xpath('//dd[@class="query_info_dd1"]/text()').extract_first()
        person_document['sex'] = person_sex

        # 证件类型
        document_type = Selector(response=response).xpath(
            '//div[@class="activeTinyTabContent"]/dl/dd[2]/text()').extract_first()
        person_document['idType'] = document_type

        # 证件编号
        ducoment_number = Selector(response=response).xpath(
            '//div[@class="activeTinyTabContent"]/dl/dd[3]/text()').extract_first()
        person_document['card'] = ducoment_number

        # 证件相关信息
        document_person = Selector(response=response).xpath('//div[@id="regcert_tab"]/dl')

        for dl in document_person:
            # 人员名称

            dt = dl.xpath('./dt')
            dl = dl.xpath('./dd')
            dl.append(dt)
            for dd in dl:
                if len(dl) == 5:
                    person_document['major'] = ''
                one_person_data = dd.xpath('./span/text()').extract_first()
                # print(one_person_data)
                if one_person_data == '注册类别：':
                    register_type = dd.xpath('./b/text()').extract_first()
                    if register_type == [] or register_type == None:
                        person_document['grade'] = ''
                    person_document['grade'] = register_type

                elif one_person_data == '注册专业：':
                    register_major = dd.xpath('text()').extract_first()
                    if register_major == [] or register_major == None:
                        person_document['major'] = ''
                    else:
                        person_document['major'] = register_major

                elif one_person_data == '证书编号：':
                    certificate_number = dd.xpath('text()').extract_first()
                    if certificate_number == [] or certificate_number == None:
                        person_document['num'] = ''
                    else:
                        person_document['num'] = certificate_number

                elif one_person_data == '执业印章号：':
                    practice_seal_number = dd.xpath('text()').extract_first()
                    if practice_seal_number == [] or practice_seal_number == None:
                        person_document['sealNum'] = ''
                    person_document['sealNum'] = practice_seal_number
                elif one_person_data == '有效期：':
                    term_of_validity = dd.xpath('text()').extract_first()
                    if term_of_validity == [] or term_of_validity is None:
                        person_document['validTime'] = ''
                    else:
                        term_of_validity = term_of_validity.replace('年', '-')
                        term_of_validity = term_of_validity.replace('月', '-')
                        term_of_validity = term_of_validity.split('日')[0]
                        person_document['validTime'] = term_of_validity

                elif one_person_data == '注册单位：':
                    registered_unit = dd.xpath('./a/text()').extract_first()
                    if registered_unit == [] or registered_unit is None:
                        person_document['companyName'] = ''
                    else:
                        registered_unit = registered_unit.split()[0]
                        person_document['companyName'] = registered_unit
                # 证件信息发送一条
            person_document['token'] = self.token
            person_zz = '\t人员名称:' + person_name + '' + '添加成功\n\n'

            time.sleep(0.5)
            yield Request(url=self.tongnie, method="POST", body=json.dumps(person_document),
                          headers={'Content-Type': 'application/json'}, callback=self.zz,
                          meta={'company_name': person_document['companyName'],
                                'data': person_document}
                          )
            # logging.info(person_zz)
            logging.error(person_zz)
            print(person_document)

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
            self.r.sadd('person_error', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')
