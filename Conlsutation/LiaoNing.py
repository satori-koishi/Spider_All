from lxml import etree
import requests
import time
import sys
from skimage import io
import os
from Tool.DeBlanking import trim
from Tool.TableDisdinguish import baiduOCR

from pymongo import MongoClient
client = MongoClient('mongodb://admin:tongna888@106.12.113.52:27017/')
db = client.qualification.credit
credit = db.find_one()
print(credit)
# credit.insert_one({'company': '企业名', 'area': '省份', 'category': '类别', 'item ': '专业（业务）grade 级别'})
# credit.insert_many(credit)
# credit.insert({"name": "zhangsan", "age": 18})  # 插入一条数据，如果没出错那么说明连接成功


header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3 ',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/74.0.3729.108 Safari/537.36 ',
}
LiaoNingBigUrl = 'http://www.lpaec.com'
JilinBigUrl = 'http://www.jlaec.com.cn'
NeiMengGuBigUrl = 'http://www.nmgczx.com'
HeiLongJiangBigUrl = 'http://ljeca.com'
DalianBigUrl = 'http://www.dlaec.com.cn'


def LiaoNing():
    LiaoNingContent = requests.get(url='http://www.lpaec.com/index.php/cn/news/view/id/52/rid/1.html', headers=header)
    LiaoNingXpath = etree.HTML(LiaoNingContent.text)
    ImgList = LiaoNingXpath.xpath('//div[@class="news_con"]/p/img/@src')
    ImgList = ImgList[2:]
    functionName = sys._getframe().f_code.co_name
    if os.path.exists('./staticImg/%s' % functionName):
        for i in ImgList:
            ImgUrl = LiaoNingBigUrl + i
            byteImg = requests.get(ImgUrl)
            name = i.split('/')[-1]
            PathUrl = 'staticimg/%s/%s' % (functionName, name)
            with open(PathUrl, 'wb') as file:
                file.write(byteImg.content)
            file.close()
            address = './%s' % PathUrl
            # im = io.imread(address)
            # trim(im, address)
            # time.sleep(3)
            # baiduOCR(address)
    else:
        os.makedirs('./staticImg/%s' % functionName)
        eval(functionName)


def JILin():
    JiLinContent = requests.get(url='http://www.jlaec.com.cn/News.aspx/390', headers=header)
    JiLinContent = etree.HTML(JiLinContent.text)
    ImgList = JiLinContent.xpath('//div[@class="intro"]/p/img/@src')
    ImgList = ImgList[2:]
    functionName = sys._getframe().f_code.co_name
    if os.path.exists('./staticImg/%s' % functionName):
        for i in ImgList:
            ImgUrl = JilinBigUrl + i
            byteImg = requests.get(ImgUrl)
            name = i.split('/')[-1]
            PathUrl = 'staticimg/%s/%s' % (functionName, name)
            with open(PathUrl, 'wb') as file:
                file.write(byteImg.content)
            file.close()
            address = './%s' % PathUrl
            # im = io.imread(address)
            # trim(im, address)
            # time.sleep(3)
            # baiduOCR(address)
    else:
        os.makedirs('./staticImg/%s' % functionName)
        eval(functionName)


def JiangXi():
    JiLinContent = requests.get(url='http://www.jxaec.com/xhgz/tzgg/201812/t20181203_224446.htm', headers=header)
    JiLinContent = etree.HTML(JiLinContent.text)
    ImgList = JiLinContent.xpath('//p/img/@src')
    ImgList = ImgList[1:]
    functionName = sys._getframe().f_code.co_name
    if os.path.exists('./staticImg/%s' % functionName):
        for i in ImgList:
            byteImg = requests.get(i)
            name = i.split('/')[-1]
            PathUrl = 'staticimg/%s/%s' % (functionName, name)
            with open(PathUrl, 'wb') as file:
                file.write(byteImg.content)
            file.close()
            # address = './staticImg/%s' % name
            # im = io.imread(address)
            # trim(im, address)
            # time.sleep(3)
            # baiduOCR(address)
    else:
        os.makedirs('./staticImg/%s' % functionName)
        eval(functionName)


def GuiZhou():
    GuiZhouContent = requests.get(url='http://www.gpaec.com.cn/html/2018/shengnews_0920/411.html', headers=header)
    GuiZhouContent = etree.HTML(GuiZhouContent.text)
    ImgList = GuiZhouContent.xpath('//div[@class="newsDetail_content"]/img/@src')
    ImgList = ImgList[2:]
    functionName = sys._getframe().f_code.co_name
    if os.path.exists('./staticImg/%s' % functionName):
        for i in ImgList:
            byteImg = requests.get(i)
            name = i.split('/')[-1]
            PathUrl = 'staticimg/%s/%s' % (functionName, name)
            with open(PathUrl, 'wb') as file:
                file.write(byteImg.content)
            file.close()
            # address = './staticImg/%s' % name
            # im = io.imread(address)
            # trim(im, address)
            # time.sleep(3)
            # baiduOCR(address)
    else:
        os.makedirs('./staticImg/%s' % functionName)
        eval(functionName)


def NeiMengGu():
    NeiMengGuContent = requests.get(url='http://www.nmgczx.com/index.php?m=Show&a=index&cid=88&id=752', headers=header)
    NeiMengGuContent = etree.HTML(NeiMengGuContent.text)
    ImgList = NeiMengGuContent.xpath('//div[@class="xwxxy3"]/p/img/@src')
    ImgList = ImgList[2:]
    functionName = sys._getframe().f_code.co_name
    if os.path.exists('./staticImg/%s' % functionName):
        for i in ImgList:
            ImgUrl = NeiMengGuBigUrl + i
            byteImg = requests.get(ImgUrl)
            name = ImgUrl.split('/')[-1]
            PathUrl = 'staticimg/%s/%s' % (functionName, name)
            with open(PathUrl, 'wb') as file:
                file.write(byteImg.content)
            file.close()
            # address = './staticImg/%s' % name
            # im = io.imread(address)
            # trim(im, address)
            # time.sleep(3)
            # baiduOCR(address)
    else:
        os.makedirs('./staticImg/%s' % functionName)
        eval(functionName)


def HeiLongJiang():
    HeiLongJiangContent = requests.get(url='http://ljeca.com/index.php/home/newshyzx/show/id/16/classid/2.html',
                                       headers=header)
    HeiLongJiangContent = etree.HTML(HeiLongJiangContent.text)
    ImgList = HeiLongJiangContent.xpath('//div[@class="tab-content"]/div')[-1].xpath('./p/img/@src')
    ImgList = ImgList[2:]
    print(ImgList)
    functionName = sys._getframe().f_code.co_name
    if os.path.exists('./staticImg/%s' % functionName):
        for i in ImgList:
            ImgUrl = HeiLongJiangBigUrl + i
            byteImg = requests.get(ImgUrl)
            name = ImgUrl.split('/')[-1]
            PathUrl = 'staticimg/%s/%s' % (functionName, name)
            with open(PathUrl, 'wb') as file:
                file.write(byteImg.content)
            file.close()
            # address = './staticImg/%s' % name
            # im = io.imread(address)
            # trim(im, address)
            # time.sleep(3)
            # baiduOCR(address)
    else:
        os.makedirs('./staticImg/%s' % functionName)
        eval(functionName)


def DaLian():
    DaLianContent = requests.get(url='http://www.dlaec.com.cn/gonggaolan/163.html',
                                 headers=header)
    DaLianContent = etree.HTML(DaLianContent.text)
    ImgList = DaLianContent.xpath('//div[@class="news_content_content"]/p/img/@src')
    ImgList = ImgList[2:]
    print(ImgList)
    functionName = sys._getframe().f_code.co_name
    if os.path.exists('./staticImg/%s' % functionName):
        for i in ImgList:
            ImgUrl = DalianBigUrl + i
            byteImg = requests.get(ImgUrl)
            name = ImgUrl.split('/')[-1]
            PathUrl = 'staticimg/%s/%s' % (functionName, name)
            with open(PathUrl, 'wb') as file:
                file.write(byteImg.content)
            file.close()
            # address = './staticImg/%s' % name
            # im = io.imread(address)
            # trim(im, address)
            # time.sleep(3)
            # baiduOCR(address)
    else:
        os.makedirs('./staticImg/%s' % functionName)
        eval(functionName)


if __name__ == '__main__':
    start_time = time.time()
    print('开始的时间%s' % start_time)
    JILin()
    end_time = time.time()
    print('结束的时间%s' % end_time)
    print('结束的时间共用时%s' % (end_time - start_time))
