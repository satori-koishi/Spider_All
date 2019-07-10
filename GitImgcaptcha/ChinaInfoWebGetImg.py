import requests
import lxml
import time
import os
import json
from pymongo import MongoClient
import sys
from Calculation import calculation

client = MongoClient('mongodb://admin:tongna888@106.12.113.52:27017/')

mongoDB = client["CreditChina"]
log_file = open("log/shanxi.log", "w", encoding='utf-8')


# proxies = {'http': 'http://117.191.11.107:8080'}
# response = requests.get(url, proxies=proxies)


class CreditChina(object):
    def __init__(self):
        """
            pass
        """
        self.liceNumber = None
        self.companyID = None
        self.companyCid = None
        self.China = None
        self.CompanyName = None
        self.number = 100
        self.InfoUrl = 'http://www.sxcredit.gov.cn/queryClassContent.jspx'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/74.0.3729.108 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        self.ImgHeaders = {'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                         'like Gecko) '
                                         'Chrome/74.0.3729.108 Safari/537.36',
                           }

    def start_url(self, company_name):
        """
            主要的作用是第一次访问给requests的session设置上cookie以便后面方便实用~~
        :param company_name:输出公司名称获取到信息
        :return:
        """
        self.China = requests.session()
        self.CompanyName = company_name
        time.sleep(0.3)
        ajax_data = {'creditType': 'credit', 'keyWord': self.CompanyName}
        self.China.post(url='http://www.sxcredit.gov.cn/search.jspx', data=ajax_data, headers=self.headers)
        self.captcha_img_machining()

    def captcha_img_machining(self):
        """
            使用上面获取到的设置的cookie然后去访问验证码
        :return:
        """
        now_time = int(time.time() * 1000)
        img_url = 'http://www.sxcredit.gov.cn/servlet/validateCodeServlet?d=%s' % now_time

        img_content = self.China.get(url=img_url, headers=self.ImgHeaders)
        time.sleep(0.3)
        img_path = 'origin/' + str('validateCodeServlet') + '.jpg'
        with open(img_path, 'wb') as f:
            f.write(img_content.content)
        url = "http://192.168.199.208:5000/b"
        files = {'image_file': ('xxx', open(img_path, 'rb'), 'application')}
        r = requests.post(url=url, files=files)
        code = json.loads(r.text)
        print(json.loads(r.text), file=log_file)
        code = code['value']
        f.close()
        cc = calculation(code)

        # img_result = input('请在当前目录下的origin下找验证码图片并输入结果：')
        # print('请输入的：验证码结果是%s' % img_result, file=log_file)
        self.company_id(cc)

    def company_id(self, img_result):
        """
            使用img_result的结果来获取公司的ID同样要是用上面设置好的cookie,
            解刨获取到的公司信息
        :param img_result: 验证码结果
        :return:
        """
        carry_ajax_data = {'creditType': 'credit', 'keyWord': self.CompanyName, 'captcha': int(img_result)}
        search_company_url = 'http://www.sxcredit.gov.cn/queryCreditData.jspx'
        company_json = self.China.post(url=search_company_url, data=carry_ajax_data, headers=self.headers)
        company_data = json.loads(company_json.text)
        time.sleep(0.3)
        try:
            self.companyID = company_data['list'][0]['id']
            print('成功')
        except KeyError:
            self.number -= 1
            # self.captcha_img_machining()
            print('失败')
        # print('你获取到的companyID为：%s' % self.companyID, file=log_file)
        # self.pick_up_company_infos()

    def pick_up_company_infos(self):
        """
            获取到公司基本信息以及table class id等详细信息，然后存储等操作
        :return:
        """
        use_all_data = {'id': self.companyID}
        basic_url = 'http://www.sxcredit.gov.cn/queryCreditBaseInfo.jspx'
        company_basic_data = self.China.post(url=basic_url, data=use_all_data, headers=self.headers)
        company_basic_data = json.loads(company_basic_data.text)
        # print('获取到的公司基本信息：%s' % company_basic_data.text, file=log_file)
        basic_data = {'companyName': company_basic_data['list'][0]['value'],
                      'liceNumber': company_basic_data['list'][1]['value'],
                      'departmentNumber': company_basic_data['list'][2]['value'],
                      'organizationCode': company_basic_data['list'][3]['value'],
                      'taxNumber': company_basic_data['list'][4]['value'],
                      'legalName': company_basic_data['list'][5]['value'],
                      'legalIdCard': company_basic_data['list'][6]['value'],
                      'address': company_basic_data['address']}
        # b_data = {'CompanyName': self.CompanyName, 'licenseNumber': self.liceNumber, 'data': basic_data,
        #           'Province': '陕西省'}
        # ok = mongoDB['CompanyBasicInfo'].insert_one(b_data)
        # print(ok.inserted_id, file=log_file)
        print('整理之后的公司基本信息：%s' % basic_data, file=log_file)
        self.liceNumber = company_basic_data['list'][1]['value']
        table_company_url = 'http://www.sxcredit.gov.cn/queryTableClass.jspx'
        c_table_info = self.China.post(url=table_company_url, data=use_all_data, headers=self.headers)
        c_table_info = json.loads(c_table_info.text)
        # for c in c_table_info['list']:
        #     if 'tableClasses' in c.keys():
        #         data = json.loads(c['tableClasses'])
        #         for id in data:
        #             from_data = {'id': self.companyID, 'tableClassId': id['table_id']}
        #             if id['table_zh_name'] == '主体身份登记信息':
        #                 time.sleep(0.3)
        #                 self.subject_information(from_data=from_data, table_name=id['table_zh_name'])
        #
        #             elif id['table_zh_name'] == '主体身份登记变更信息':
        #                 time.sleep(0.3)
        #                 self.change_info(from_data=from_data, table_name=id['table_zh_name'])
        #
        #             elif id['table_zh_name'] == '出资人及出资信息':
        #                 time.sleep(0.3)
        #                 self.shareholder_info(from_data=from_data, table_name=id['table_zh_name'])
        #
        #             elif id['table_zh_name'] == '主要人员信息':
        #                 time.sleep(0.3)
        #                 self.shareholder_info(from_data=from_data, table_name=id['table_zh_name'])
        #
        #             elif id['table_zh_name'] == '行政许可信息':
        #                 time.sleep(0.3)
        #                 self.admin_info(from_data=from_data, table_name=id['table_zh_name'])
        #
        #             elif id['table_zh_name'] == '行政处罚信息':
        #                 time.sleep(0.3)
        #                 self.principal_person(from_data=from_data, table_name=id['table_zh_name'])
        #
        #             elif id['table_zh_name'] == '列入经营异常名录信息':
        #                 time.sleep(0.3)
        #                 self.principal_person(from_data=from_data, table_name=id['table_zh_name'])
        #
        #             elif id['table_zh_name'] == '双随机抽查结果信息':
        #                 time.sleep(0.3)
        #                 self.random_info(from_data=from_data, table_name=id['table_zh_name'])

    # def get_data(self, class_id, class_name):
    #     from_data = {'tableClassId': class_id, 'id': self.companyID}
    #     print('当前是:%s----的信息' % class_name, file=log_file)
    #     data = self.China.post(url=self.InfoUrl, data=from_data, headers=self.headers)
    #
    #     print(json.loads(data.text), file=log_file)

    def subject_information(self, from_data, table_name):
        basic_data = self.China.post(url=self.InfoUrl, data=from_data, headers=self.headers)
        print('以下为%s详细信息:' % table_name, file=log_file)
        basic_data = json.loads(basic_data.text)
        data = {'CompanyName': self.CompanyName, 'licenseNumber': self.liceNumber, 'data': basic_data,
                'Province': '陕西省'}
        print(data, file=log_file)
        # ok = mongoDB['SubjectInfo'].insert_one(data)
        # print(ok.inserted_id, table_name, file=log_file)

    def change_info(self, from_data, table_name):
        change_data = self.China.post(url=self.InfoUrl, data=from_data, headers=self.headers)
        print('以下为%s详细信息:' % table_name, file=log_file)
        change_data = json.loads(change_data.text)
        print(change_data, file=log_file)
        data = {'CompanyName': self.CompanyName, 'licenseNumber': self.liceNumber, 'data': change_data,
                'Province': '陕西省'}
        # ok = mongoDB['CompanyChangeInfo'].insert_one(data)
        # print(ok.inserted_id, table_name, file=log_file)

    def shareholder_info(self, from_data, table_name):
        shareholder_data = self.China.post(url=self.InfoUrl, data=from_data, headers=self.headers)
        print('以下为%s详细信息:' % table_name, file=log_file)
        shareholder_data = json.loads(shareholder_data.text)
        print(shareholder_data, file=log_file)
        data = {'CompanyName': self.CompanyName, 'licenseNumber': self.liceNumber, 'data': shareholder_data,
                'Province': '陕西省'}
        # ok = mongoDB['ShareholderInfo'].insert_one(data)
        # print(ok.inserted_id, table_name, file=log_file)

    def principal_person(self, from_data, table_name):
        principal_data = self.China.post(url=self.InfoUrl, data=from_data, headers=self.headers)
        print('以下为%s详细信息:' % table_name, file=log_file)
        principal_data = json.loads(principal_data.text)
        print(principal_data, file=log_file)
        data = {'CompanyName': self.CompanyName, 'licenseNumber': self.liceNumber, 'data': principal_data,
                'Province': '陕西省'}
        # ok = mongoDB['PrincipalPersonInfo'].insert_one(data)
        # print(ok.inserted_id, table_name, file=log_file)

    def admin_info(self, from_data, table_name):
        admin_data = self.China.post(url=self.InfoUrl, data=from_data, headers=self.headers)
        print('以下为%s详细信息:' % table_name, file=log_file)
        admin_data = json.loads(admin_data.text)
        data = {'CompanyName': self.CompanyName, 'licenseNumber': self.liceNumber, 'data': admin_data,
                'Province': '陕西省'}
        # ok = mongoDB['AdministrativeInfo'].insert_one(data)
        # print(ok.inserted_id, table_name, file=log_file)

        print(admin_data, file=log_file)

    def abnormal_operation(self, from_data, table_name):
        abnormal_data = self.China.post(url=self.InfoUrl, data=from_data, headers=self.headers)
        print('以下为%s详细信息:' % table_name, file=log_file)
        abnormal_data = json.loads(abnormal_data.text)
        print(abnormal_data, file=log_file)
        data = {'CompanyName': self.CompanyName, 'licenseNumber': self.liceNumber, 'data': abnormal_data,
                'Province': '陕西省'}
        # ok = mongoDB['AbnormalOperation'].insert_one(data)
        # print(ok.inserted_id, table_name, file=log_file)

    def random_info(self, from_data, table_name):
        random_data = self.China.post(url=self.InfoUrl, data=from_data, headers=self.headers)
        print('以下为%s详细信息:' % table_name, file=log_file)
        random_data = json.loads(random_data.text)
        print(random_data, file=log_file)
        data = {'CompanyName': self.CompanyName, 'licenseNumber': self.liceNumber, 'data': random_data,
                'Province': '陕西省'}
        # ok = mongoDB['RandomCheckInfo'].insert_one(data)
        # print(ok.inserted_id, table_name, file=log_file)

    def punish_info(self, from_data, table_name):
        punish_data = self.China.post(url=self.InfoUrl, data=from_data, headers=self.headers)
        print('以下为%s详细信息:' % table_name, file=log_file)
        punish_data = json.loads(punish_data.text)
        print(punish_data, file=log_file)
        data = {'CompanyName': self.CompanyName, 'licenseNumber': self.liceNumber, 'data': punish_data,
                'Province': '陕西省'}
        # ok = mongoDB['AdministrativeSanction'].insert_one(data)
        # print(ok.inserted_id, table_name, file=log_file)

    def start(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            for i in f.readlines():
                name = i.replace('\n', '')
                self.start(name)


company = CreditChina()
for i in range(100):
    company.start_url('西安东旭景观建设工程有限公司')
    print('共一百次查看成功多少次%s' % company.number, file=log_file)
print('成功率%s' % (company.number/100))

