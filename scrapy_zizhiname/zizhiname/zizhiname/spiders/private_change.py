# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
from scrapy.http import Request
import requests
import json
class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    name = 'private_change'
    # 起始网站
    def start_requests(self):
        """爬虫起始"""
        self.token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'
        # 本公司接口
        self.tongnie = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompanyEngineer.htm'
        # 起始url
        self.big_url = 'http://jzsc.mohurd.gov.cn'
        # form表单url
        self.url = 'http://jzsc.mohurd.gov.cn/dataservice/query/comp/list'
        # 提交form数据
        self.corporate_name = '西安匠伦建筑设计有限公司'
        self.mycontinue = True
        # 访问并携带参数
        return [scrapy.FormRequest(self.url,
                                   formdata={'qy_name': self.corporate_name},
                                   callback=self.parse)]
    # 选择公司
    def parse(self, response):
        # 进入当前公司
        """选择公司"""
        corporate_url = Selector(response=response).xpath('//td[@class="text-left primary"]/a/@href').extract_first()
        url = self.big_url + corporate_url
        return Request(url=url, callback=self.detailed_information)
    # 拿到公司人员ajxs的数据
    def detailed_information(self, response):
        """人员基本信息表"""
        url = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li[2]/a/@data-url').extract_first()
        # print(url)
        url = self.big_url + url
        return Request(url=url, callback=self.person)
    # 拿到每个人员的url地址
    def person(self,response):
        """当前公司所有人员url"""
        # 获取当前表里的所有数据
        tr = Selector(response=response).xpath('//tbody/tr')
        # 获取当前有多少数据
        all_date = Selector(response=response).xpath('//div[@class="comp_regstaff_links"]/a[1]/span/text()').extract_first()
        # 去除不需要的
        one_name = Selector(response=response).xpath('//tbody/tr[1]/td[2]/a/text()').extract_first()
        all_date = all_date.replace('）', '')
        all_date = int(all_date.replace('（', ''))
        if all_date == 0:
            return 'zz'
        if all_date < 26:
            print('无分页')
            self.mycontinue = False
        # 算出有能有多少页
        self.page = all_date//25 + 2
        # 拿出所有的人员的A标签属性
        for r in tr:
            one_person = r.xpath('./td/a/@onclick').extract_first()
            if not one_person == None:
                person_url = one_person.split('top.window.location.href=\'')[1]
                person_url = person_url.split('\'')[0]
                person_url = self.big_url + person_url

                yield Request(url=person_url, callback=self.person_detailed)

            # 查看是否有分页
        another_page = Selector(response=response).xpath('//div[@class="clearfix"]')
        # 如果不够分页或者，没有分页选择器这不执行
        if not another_page == [] and self.mycontinue:
            for a in range(2, self.page):
                print(a)
                a = str(a)
                yield scrapy.FormRequest(response.url, formdata={'$pg': a}, callback=self.person)
            # 只循环一次
            self.mycontinue = False
    # 获取执业注册信息
    def person_detailed(self,response):
        """人员证件详细表"""
        person_document = {}
        person_document['companyName '] = self.corporate_name
        # 人员名称
        person_name = Selector(response=response).xpath('//div[@class="user_info spmtop"]/b/text()').extract_first()
        person_document['name'] = person_name
        another_imformation = Selector(response=response).xpath('//ul[@class="tinyTab datas_tabs"]/li[6]/a/@data-url').extract_first()
        from ..items import ZizhinameItem
        item = ZizhinameItem()
        item['name'] = person_name
        yield Request(url=self.big_url+another_imformation, callback=self.change_person_data,meta={'item': item})
    def change_person_data(self, response):
        """变更记录表数据"""
        change_data = {}
        # 发送变更记录表
        person_name = response.meta['item']['name']
        name = '变更记录'
        print(name, 'zz')
        change_data['person_name'] = person_name
        grade = Selector(response=response).xpath('//tbody/tr/td[1]/text()').extract_first()
        grade = grade.split(' ')[0]
        if grade == '暂未查询到已登记入库信息':
            print('暂时无数据')
        else:
            change_data['grade'] = grade
            now_company = Selector(response=response).xpath('//div[@class="curQy"]/span/text()').extract_first()
            change_data['now_company'] = now_company

            change_record = Selector(response=response).xpath('//ul[@class="cbp_tmtimeline"]/li')
            # print(change_record)
            myset = set()
            for c in change_record:
                year = c.xpath('./div[1]/span[1]/text()').extract_first()
                month_day = c.xpath('./div[1]/span[2]/text()').extract_first()
                year = year.split('年')[0]
                month_day = month_day.split('/')
                month = month_day[0]
                day = month_day[1]

                # 时间
                date = year + month + day
                date = int(date)
                date = date*10+1
                if date in myset:
                    date += 1
                myset.add(date)

                change_data['not_data'] = date

                # 原来的公司
                original_company = c.xpath('./div[@class="cbp_tmlabel"]/p/span[1]/text()').extract_first()
                change_data['original_company'] = original_company

                # 现在的公司
                now_z_company = c.xpath('./div[@class="cbp_tmlabel"]/p/span[2]/text()').extract_first()
                change_data['now_z_company'] = now_z_company
                change_data['name_company'] = self.corporate_name
                print(change_data)
                print('一条信息')
                # 每条变更记录发送一条
                # yield Request()
    # 发送给服务器反映
    def zz(self, response):
        print(response.text)

