# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                          'Chrome/74.0.3729.108 Safari/537.36'}
# test = China.post(url='http://www.sxcredit.gov.cn/search.jspx', headers=headers,
#                   data={'creditType': 'credit', 'keyWord': '中北'})
#
# # now_time = int(time.time() * 1000)
# url = 'http://www.sxcredit.gov.cn/servlet/validateCodeServlet?d=%s' % now_time
# headers2 = {'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                           'Chrome/74.0.3729.108 Safari/537.36',
#             }
# ChinaCompanyInfoShanXi = China.get(url=url, headers=headers2)
# ImgPath = 'origin/' + str(now_time) + '.jpg'
# with open(ImgPath, 'wb') as file:
#     file.write(ChinaCompanyInfoShanXi.content)
# file.close()
#
# captcha = input('请输入验证码')
# data = {'creditType': 'credit',
#         'keyWord': '中北', 'captcha': int(captcha),
#         }
# CompanyData = China.post(url='http://www.sxcredit.gov.cn/queryCreditData.jspx',
#                          headers=headers, data=data)
# xx = json.loads(CompanyData.text)
# CompanyID = xx['list'][0]['id']
# print(CompanyID)
# InformationUrl = 'http://www.sxcredit.gov.cn/queryCreditBaseInfo.jspx'
# CInfo = China.post(url=InformationUrl, data={'id': CompanyID}, headers=headers)
# print(CInfo.text)
# TableCompanyUrl = 'http://www.sxcredit.gov.cn/queryTableClass.jspx'
# CTableInfo = China.post(url=TableCompanyUrl, data={'id': CompanyID}, headers=headers)
# print(CTableInfo.text)