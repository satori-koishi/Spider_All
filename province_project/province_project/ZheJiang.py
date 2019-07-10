from scrapy import Selector
from lxml import etree
import requests

index = 1


def bb(response):
    company_info = etree.HTML(response.text)
    company_name = company_info.xpath('//td[@colspan="5"]/text()')[0]
    tr = company_info.xpath('//tr[@class="auto_h"]/td/div/a/@href')
    print(tr)
    for t in tr:
        url = 'http://115.29.2.37:8080' + t
        cc = requests.get(url=url, headers=headers)
        xx = etree.HTML(cc.text)
        info(xx, company_name)


def info(response, company_name):
     name = response.xpath('//td[@colspan="5"]/text()')
     print(name)


def start(nn):
    global index
    global headers

    tr = nn.xpath('//table[@class="t1"]/tr')
    tr = tr[1:-1]
    for t in tr:
        td = t.xpath('./td')
        url = td[1].xpath('./div/a/@href')[0]
        url = 'http://115.29.2.37:8080/' + url
        info = requests.get(url=url, headers=headers)
        bb(info)
    zzz = nn.xpath('//span[@class="vcountPage"]/text()')[0]
    page = nn.xpath('//div[@id="pagebar"]/ul/li[3]/@alt')[0]
    index += 1
    if int(zzz) != index:
        xx = requests.post(url='http://115.29.2.37:8080/enterprise_ajax.php', headers=headers,
                           data={'page': page})
        tt = etree.HTML(xx.text)
        start(tt)


headers = {'Accept': 'text/html, */*; q=0.01',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.9',
           'Connection': 'keep-alive',
           'Host': '115.29.2.37:8080',
           'Origin': 'http://115.29.2.37:8080',
           'Referer': 'http://115.29.2.37:8080/enterprise.php',
           'X-Requested-With': 'XMLHttpRequest',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'
           }
cc = requests.get(url='http://115.29.2.37:8080/enterprise_ajax.php', headers=headers, )
nn = etree.HTML(cc.text)
start(nn)