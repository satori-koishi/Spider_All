import requests
#
token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
person_data = {'companyName': '坤鹏志远建设工程有限公司',
               'licenseNum': '', 'name': '   杨晗芝', 'area': '青海省', 'sex': '',
               'idCard': '5002351993******81', 'grade': '二级注册建造师', 'major': '公路工程,建筑工程',
               'num': '川251151622255', 'regNum': ' ',
               'validTime': '2017-2-1', 'tel': '', 'tokenKey': token
               }

test = requests.post(data=person_data,
                     url='https://api.maotouin.com/rest/companyInfo/addCompanyRecordEngineer.htm'
                     # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecordEngineer.htm'
                     )
print(test.text)

import json
# company_data = {'companyName': '坤鹏志远建设工程有限公司',
#                 'licenseNum': '91510100MA6DFPXK34', 'area': '青海省',
#                 'companyArea': '', 'contactAddress': '',
#                 'contactMan': '', 'contactPhone': '', 'token': token
#                 }
# test = requests.post(
#                      data=json.dumps(company_data),
#                      # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm'
#                      url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
#                      headers={'Content-Type': 'application/json'},
#                      # url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm'
#                      )
#
# print(test.text)


import json
# company_data = {'name': '坤鹏志远建设工程有限公司',
#                 'regNo': '',
#                 'manageState': '',
#                 'manageStateCN': '',
#                 'legalMan': '',
#                 'alias': '坤鹏志远建设工程有限公司',
#                 'licenseNum': '91510100MA6DFPXK34',
#                 'tokenKey': token,
#                 }
# test = requests.post(
#                      data=company_data,
#                      # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm'
#                      url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyInfo.htm',
#                      # headers={'Content-Type': 'application/json'},
#                      # url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm'
#                      )

# print(test.text)

