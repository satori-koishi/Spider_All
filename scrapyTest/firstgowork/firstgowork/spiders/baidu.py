# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy import Selector
from firstgowork import items

class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    # allowed_domains = ['baidu.com']
    start_urls = ['http://www.bmlink.com']

    def parse(self, response):
        item = items.JiandanItem()
        item['image_urls'] = response.xpath('//img//@src').extract() #提取图片链接
        yield item
        yield Request(

        )




import scrapy
from douban.items import DoubanItem
from faker import Factory
import urlparse
f = Factory.create()

class CommentSpider(scrapy.Spider):
    name = "comment_spider"
    start_urls = [
        #'https://movie.douban.com/chart'
        'https://www.douban.com'
        ]

    formdata={
        'form_email': 'he__v5@163.com',
        'form_password': 'Glory05&',
        # 'captcha-solution': '',
        # 'captcha-id': '',
        #'login': '登录',
        #'redir': 'https://www.douban.com/',
        'source':'index_nav'
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        #'Host': 'accounts.douban.com',
        #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
        'User-Agent': f.user_agent()
    }

    def start_requests(self):
        return [scrapy.Request(url='https://www.douban.com/accounts/login',
                               headers=self.headers,
                               meta={'cookiejar': 1},
                               callback=self.parse_login)]

    def parse_login(self, response):
        # 如果有验证码要人为处理
        if 'captcha_image' in response.body:
            print ('Copy the link:')
            link = response.xpath('//img[@class="captcha_image"]/@src').extract()[0]
            print (link)
            captcha_solution = input('captcha-solution:')
            captcha_id = urlparse.parse_qs(urlparse.urlparse(link).query, True)['id']
            self.formdata['captcha-solution'] = captcha_solution
            self.formdata['captcha-id'] = captcha_id
        return [scrapy.FormRequest.from_response(response,
                                                 formdata=self.formdata,
                                                 headers=self.headers,
                                                 meta={'cookiejar': response.meta['cookiejar']},
                                                 callback=self.after_login
                                                 )]

    def after_login(self, response):
        #站内的测试链接，用来判断是否登入成功
        test_url = "https://www.douban.com/people/90868630/"
        if response.url==test_url:
            if response.status==200:
                print '***************'
                print u'登录成功'
                print '***************\n'
            else:
                print '***************'
                print u'登录失败'
                print '***************\n'

        yield scrapy.Request(test_url,
                      meta={'cookiejar': response.meta['cookiejar']},
                      headers=self.headers,
                      callback=self.after_login)

        #self.headers['Host'] = "www.douban.com"
        yield scrapy.Request(url='https://movie.douban.com/chart',
                              meta={'cookiejar': response.meta['cookiejar']},
                              headers=self.headers,
                              callback=self.parse_movie_url)



    #def start_requests(self):
    #    return [scrapy.Request(url='https://movie.douban.com/chart',
    #                           headers=self.headers,
    #                           callback=self.parse_movie_url)]

    def parse_movie_url(self, response):

        for movie_url in response.xpath('.//div[@class="article"]/div/div/table//td[1]//a[@class]/@href').extract():
            #yield {'url':movie_url}
            yield scrapy.Request(movie_url,headers=self.headers,callback=self.parse_comments_url)

    def parse_comments_url(self,response):
        comment_url=response.xpath('.//div[@id="comments-section"]/div/h2/span/a/@href').extract_first()
        #yield {'url':comment_url}
        yield scrapy.Request(comment_url,headers=self.headers,callback=self.parse_comments)

    def parse_comments(self,response):
        print response.status
        print response.url
        movie_name=response.xpath('.//div[@id="content"]/h1/text()').extract_first()
        comments=response.xpath('.//div[@class="article"]/div[@class="mod-bd"]/div[@class="comment-item"]/div[@class="comment"]')
        next_page=response.xpath('//div[@id="paginator"]//a[@class="next"]')

        for comment in comments:
            user_name=comment.xpath('./h3/span[2]/a/text()').extract_first()
            star=comment.xpath('./h3/span[2]/span[2]/@class').extract_first()
            comment_content=comment.xpath('./p/text()').extract_first()
            item=DoubanItem()
            item['movie']=movie_name
            item['user']=user_name
            item['star']=star
            item['comment']=comment_content
            yield item

        if(len(next_page)!=0):
            next_page_url=response.urljoin(next_page.xpath('./@href').extract_first())
            print '\n\n'
            print next_page_url
            print '\n\n'
            yield scrapy.Request(next_page_url,headers=self.headers,callback=self.parse_comments)
            return [scrapy.FormRequest.from_response(response,
                                                 formdata=self.formdata,
                                                 headers=self.headers,
                                                 meta={'cookiejar': response.meta['cookiejar']},
                                                 callback=self.after_login
                                                 )]


class YourSpiderSpider(scrapy.Spider):
    name = 'your_spider'
    allowed_domains = ['douban.com']
    #start_urls = ['http://douban.com/']
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36"} #供登录模拟使用
    
    def start_requests(self):
        url='https://www.douban.com/accounts/login'
        #return [Request(url=url,meta={"cookiejar":1},callback=self.parse)]#可以传递一个标示符来使用多个。如meta={'cookiejar': 1}这句，后面那个1就是标示符
        return [scrapy.FormRequest("https://accounts.douban.com/login", headers=self.headers, meta={"cookiejar":1}, callback=self.parse)]
    
    
    def get_content(self, response):
            title = response.xpath('//title/text()').extract()[0]
            if u'登录豆瓣' in title:
                print("登录失败，请重试")
            else:
                print("登陆成功")

    def parse(self, response):
        
        captcha = response.xpath('//*[@id="captcha_image"]/@src').extract()
        print(captcha)
        if len(captcha)>0:
            #有验证码，人工输入验证码
            urllib.request.urlretrieve(captcha[0],filename=r"C:\Users\LBX\your_project\simulate_login\simulate_login\captcha.png")
            captcha_value=input('查看captcha.png,有验证码请输入:')
            data={
                    "form_email":"18353113181@163.com",
                    "form_password":"9241113minda",
                    "captcha-solution":captcha_value,
                    }
        else:
            #此时没有验证码
            print("无验证码")
            data={
                    "form_email":"18353113181@163.com",
                    "form_password":"9241113minda",
                                        }
        print("正在登陆中.....")
        #进行登录
        return[
                FormRequest.from_response(
                        response,
                        meta={"cookiejar":response.meta["cookiejar"]},
                        headers=self.headers,
                        formdata=data,
                        callback=self.get_content,
                        )
                ]
               


