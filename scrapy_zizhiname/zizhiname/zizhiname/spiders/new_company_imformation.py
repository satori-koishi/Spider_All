import scrapy
from scrapy import Selector
from scrapy.http import Request,Response
import requests
import json
import redis
from .. import items
class AllXinliangSpider(scrapy.Spider):
    # 执行名称
    name = 'new_company_imformation'
    def obtain_company_name_redis(self):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.company_list = []
        redis_len = r.scard('company_name')
        while redis_len != 0:
            for index in range(redis_len):
                if not index == 1000:
                    name = r.spop("company_name")

                    self.company_list.append(name)
                break
            self.company_list = []
    def start_requests(self):
        self.tongna_API = ''
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; LDN-AL00 Build/HUAWEILDN-AL00; wv)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36'
                          ' Html5Plus/1.0',
        }
        self.url =  'https://app.gsxt.gov.cn/gsxt/cn/gov/saic/web/controller/PrimaryInfoIndexAppController/search?page=1'
        # 提交form数据
        self.obtain_company_name_redis()
        for company_name in self.company_list:
            data = {"searchword": company_name,
                    "sourceType": "I"}
            return [scrapy.FormRequest(self.url, formdata=data, callback=self.parse, headers=self.headers)]

    def parse(self, response):
        response1 = json.loads(response.text)
        data1 = response1['data']['result']['data']
        first_data = data1[0]
        one_pripid = first_data['pripid']
        one_nodenum = first_data['nodeNum']
        one_enttype = first_data['entType']
        url = 'http://app.gsxt.gov.cn/gsxt/corp-query-entprise-info-primaryinfoapp-entbaseInfo-' \
              + one_pripid + '.html?nodeNum=' + str(one_nodenum) + '&entType=' + str(one_enttype)
        yield scrapy.FormRequest(url=url, headers=self.headers, callback=self.company_data)

    def company_data(self, response):
        json_after_data = json.loads(response.text)
        zz = json_after_data['result']
        company_dict = {}

        company_dict['companyName'] = zz['entName']
        # 状态
        company_dict['regState_CN'] = zz['regState_CN']
        # 统一社会信用代码
        company_dict['uniscId'] = zz['uniscId']
        # 成立日期
        company_dict['estDate'] = zz['estDate']
        # 住所
        company_dict['dom'] = zz['dom']
        # 类型
        company_dict['entType_CN'] = zz['entType_CN']
        # 开始日期
        company_dict['opFrom'] = zz['opFrom']
        # 结束日期
        company_dict['opTo'] = zz['opTo']
        # 核准日期
        company_dict['apprDate'] = zz['apprDate']
        # 登记机关
        company_dict['regOrg_CN'] = zz['regOrg_CN']
        # 注册资本
        company_dict['entType_CN'] = zz['regCap']
        # 经营范围
        company_dict['opScope'] = zz['opScope']
        data_api = json.dumps(company_dict)
        print(data_api)
        yield scrapy.FormRequest(url=self.tongna_API, callback=self.zz, formdata=data_api)

    def zz(self, response):
        print(response.text)
