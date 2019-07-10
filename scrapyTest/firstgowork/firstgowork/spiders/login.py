# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request,FormRequest
import re

class PachSpider(scrapy.Spider):                            #定义爬虫类，必须继承scrapy.Spider
    name = 'pach'                                           #设置爬虫名称
    allowed_domains = ['dig.chouti.com']                    #爬取域名
    # start_urls = ['']                                     #爬取网址,只适于不需要登录的请求，因为没法设置cookie等信息

    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'}  #设置浏览器用户代理

    def start_requests(self):
        """第一次请求一下登录页面，设置开启cookie使其得到cookie，设置回调函数"""
        return [Request('http://dig.chouti.com/',meta={'cookiejar':1},callback=self.parse)]


    def parse(self, response):
        # 响应Cookies
        Cookie1 = response.headers.getlist('Set-Cookie')                            #查看一下响应Cookie，也就是第一次访问注册页面时后台写入浏览器的Cookie
        print('后台首次写入的响应Cookies：',Cookie1)

        data = {                                                                    # 设置用户登录信息，对应抓包得到字段
            'phone': '8615284816568',
            'password': '279819',
            'oneMonth': '1'
        }

        print('登录中....!')
        """第二次用表单post请求，携带Cookie、浏览器代理、用户登录信息，进行登录给Cookie授权"""
        return [FormRequest.from_response(response,
                                          url='http://dig.chouti.com/login',                        #真实post地址
                                          meta={'cookiejar':response.meta['cookiejar']},
                                          headers=self.header,
                                          formdata=data,
                                          callback=self.next,
                                          )]


    def next(self,response):
        # 请求Cookie
        Cookie2 = response.request.headers.getlist('Cookie')
        print('登录时携带请求的Cookies：',Cookie2)

        jieg = response.body.decode("utf-8")   #登录后可以查看一下登录响应信息
        print('登录响应结果：',jieg)

        print('正在请需要登录才可以访问的页面....!')

        """登录后请求需要登录才能查看的页面，如个人中心，携带授权后的Cookie请求"""
        yield Request('http://dig.chouti.com/user/link/saved/1',meta={'cookiejar':True},callback=self.next2)


    def next2(self,response):
        # 请求Cookie
        Cookie3 = response.request.headers.getlist('Cookie')
        print('查看需要登录才可以访问的页面携带Cookies：',Cookie3)

        leir = response.xpath('//div[@class="tu"]/a/text()').extract()  #得到个人中心页面
        print('最终内容',leir)
        leir2 = response.xpath('//div[@class="set-tags"]/a/text()').extract()  # 得到个人中心页面
        print(leir2)





from scrapy.http.cookies import CookieJar    # 该模块继承自内置的http.cookiejar,操作类似

# 实例化一个cookiejar对象
cookie_jar = CookieJar()

# 首先是cookie的提取
class MySpider(scrapy.Spider):
    ....
    ....
    # 模拟登陆,之后调用一个检查是否登录成功的函数
    def login(self, response):
        ....
        return [scrapy.FormRequest(
            url=login_url,
            formdata = {'username':xxx, 'password':xxx},
            callback = self.check_login
        )]

def check_login(self, response):
    if 登录成功:
        # 到这里我们的登录状态已经写入到response header中的'Set-Cookies'中了,
        # 使用extract_cookies方法可以提取response中的cookie
        cookiejar.extract_cookies(response, response.request)
        # cookiejar是类字典类型的,将它写入到文件中
        with open('cookies.txt', 'w') as f:
            for cookie in cookie_jar:
                f.write(str(cookie) + '\n')

# 有些情况可能在发起登录之前会有一些请求,会陆续的产生一些cookie,可以在第一次请求的时候将cookiejar写入到request的meta中进行传递
scrapy.Request(url, callback=self.xxx, meta={'cookiejar': cookiejar})
# 之后每次需要传递这个cookiejar对象可以从response.meta中拿到
scrapy.Request(url, callback=self.xxx, meta={'cookiejar': response.meta['cookiejar']})

# 从本地文件中读取Cookie

     with open('cookies.txt', 'r') as f:
         cookiejar = f.read()
         p = re.compile(r'<Cookie (.*?) for .*?>')
         cookies = re.findall(p, cookiejar)
         cookies = (cookie.split('=', 1) for cookie in cookies)
         cookies = dict(cookies)
# 之后可以在第一次发起请求(start_request)时将cookie手动添加到scrapy.Request的cookies参数中,cookie在后续的请求中会自行流转.

scrapy.Request(url, callback=self.xxx, cookies=cookies)