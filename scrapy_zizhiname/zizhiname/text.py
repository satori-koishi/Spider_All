# # # from selenium import webdriver
# # # # 声明游览器类型
# # # # browser = webdriver.Chrome()
# # #
# # # browser = webdriver.Firefox()
# from  selenium import webdriver
# import requests
# from bs4 import BeautifulSoup
# import time
# # browser = webdriver.Chrome()
# # browser.get('https://www.baidu.com/')
# # print(browser.title)
# # browser.quit()
#
# # headers = {
# #     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
# # }
# #
# # data = requests.get("https://tieba.baidu.com/index.html",headers=headers)
# # html= BeautifulSoup(data.text, 'lxml')
#
#
#
# # 要使用selenium先需要定义一个具体browser对象，这里就定义的时候就看你电脑安装的具体浏览器和安装的哪个浏览器的驱动。这里以火狐浏览器为例：
# from selenium import webdriver
# zz = webdriver.Chrome()
# # 再模拟打开贴吧首页：
#
# # browser.get("https://tieba.baidu.com/f?ie=utf-8&kw=李毅&fr=search")
# # browser.set_window_size(111,222)
# # print('设置游览器大小')
# # browser.quit()
# # print('访问第一个网站')
# # zz.get('https://www.baidu.com/')
# # print('访问第二个网站')
# # zz.get('https://www.toutiao.com/')
# # print('后退到第一个网站')
# # zz.back()
# # print('前进到第二个访问的网站')
# # zz.forward()
#
# # zz.get('https://www.toutiao.com/')
# # print('刷新页面')
# # zz.refresh()
# # zz.quit()
#
# # zz.get('https://www.baidu.com/')
# # 清除文输入框的数据
# # zz.find_element_by_xpath('input[@id="kw"]').clear()
# # 选择输入框添加sand_keys
# # zz.find_element_by_xpath('//input[@id="kw"]').send_keys('三和')
# # 点击操作
# # zz.find_element_by_xpath('//input[@id="su"]').click()
# # zz.quit()
#
# # zz.get('https://www.baidu.com/')
# # zz.find_element_by_xpath('//input[@id="kw"]').send_keys('三和大神')
# # # 一样的form提交数据
# # zz.find_element_by_xpath('//input[@id="su"]').submit()
#
# # zz.get('https://www.baidu.com/')
# # zz.find_element_by_xpath('//input[@id="kw"]').send_keys('三和大神')
# # zz.find_element_by_xpath('//input[@id="su"]').click()
# # url = zz.find_element_by_xpath('//div[@id="1"]/h3/a').get_attribute('href')
# # print('zzz')
# # print(url)
# # print('zzz')
#
# # from selenium.webdriver.common.action_chains import ActionChains
# #
# # zz.get('https://www.baidu.com/')
# # zz.find_element_by_xpath('')
# # above = zz.find_element_by_link_text("设置")
# # ActionChains(above).move_to_element(above).perform()
#
#
#
# #调用环境变量指定的PhantomJS浏览器创建浏览器对象
# driver = webdriver.PhantomJS()
# driver.set_window_size(1366, 768)
# #如果没有在环境变量指定PhantomJS位置
# #driver = webdriver.PhantomJS(executable_path = "./phantomjs")
#
#
#
#
#
# a = '0'
# a = int(a)
# print(a)

# request.url == 'http://192.168.199.188:8080/web/rest/companyInfo/addCompanyBadCredit.htm'or
# request.url == 'http://192.168.199.188:8080/web/rest/companyInfo/addCompany.htm'):
import re
# post_url = 'http//192.168.199.188:8080/web/rest/companyInfo/addCompanyBadCredit.htm'
# # z = re.match('http//192.168.188:8080(.*?).htm', post_url)
# # print(z)
# z = post_url.startswith('http//192.168.199.188:8080/')
# print(z)
#
# # post_url = 'http//192.168.199.188:8080/web/rest/companyInfo/addCompanyBadCredit.htm'
# my_url = 'http://192.168.199.188:8080/web/rest/companyInfo/addCompanyBadCredit.htm'
#
#
#
#
#
# print('ssss')
# print('zzzz')


import redis
# pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
# r = redis.Redis(connection_pool=pool)
# # zz = r.sadd('company_black_code', '福建源梁建设工程有限公司')
# zz = r.sadd('company_respect', '江苏金厦建设集团有限公司')
# print(r.scard('company_respect'))
# # for s in zz:
# #     print(s.decode('utf8'))
#
# import re
#
# vv = '《福建省住房和城乡建设厅关于公布第三批建筑市场主体“黑名单”的通知》（闽建筑（2019）7号）'
# bb = '(.*?)（(.*)）'
#
# xx = re.findall(bb, vv)
# print(xx,)
# while 1:
#     print('ada')
# # print('GGGGGGG')