from aip import AipOcr
import json
import time
from pymongo import MongoClient
from skimage import io

client = MongoClient('mongodb://admin:tongna888@106.12.113.52:27017/')
cerditdb = client.qualification.credit

APP_ID = '16657913'
API_KEY = 'SNbBvp0R4Lbu6DqssoTnUGc0'
SECRECT_KEY = 'hp4tO0XDGDSFZ5tLbSbV68qgDvn4fENL'
client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)
specialList = ['PPP专项资信', '建筑', '市政公用工程', '农业、林业', '其他(旅游工程)', '其他(商物粮)', '石化、化工、医药',
               '电子、信息工程(含通信、广电、信息化)', '电力(含火电、水电、核电新能源)', '轻工、纺织', '生态建设和环境工程',
               '电力(含火电、水电、核电、新能源)', '水利水电', '冶金(含钢铁、有色)', '机械(含智能制造)', '生态建设环境工程',
               '铁路、城市轨道交通', '水文地质、工程测量、岩土工程'
               ]

typeList = ['专业资信', '专业预评价']

gradeList = ['乙级', '乙级预评价']

companyName = {'限': '公司', '有': '限公司', '公': '司', '测': '设计院有限公司', '研': '究院有限公司',
               '任': '公司', '市': '城乡道路交通发展研究中心)'
               }


def baiduOCR(address):
    i = open(address, 'rb')
    img = i.read()
    message = client.tableRecognitionAsync(img)
    print(message)
    requestId = message['result'][0]['request_id']
    time.sleep(10)
    MongoAD(requestId)


def MongoAD(requestId):
    options = {"result_type": "json", "language_type": "CHN_ENG"}
    xx = client.getTableRecognitionResult(requestId, options)
    boyd = json.loads(xx['result']['result_data'])
    print(boyd)
    number = len(boyd['forms'][0]['body']) // 5
    print(number, '行数')
    kk = []
    for i in range(number):
        if i:
            company = {}
            for data in boyd['forms'][0]['body']:
                if data['row'][0] == i:
                    if 1 == data['column'][0]:
                        if len(data['word']) > 7:
                            for key, value in companyName.items():
                                cc = data['word'][-1]
                                if cc == key:
                                    company['company'] = data['word'] + value
                                    break
                                else:
                                    company['company'] = data['word']
                        else:
                            company['company'] = ''
                    if 2 == data['column'][0]:
                        company['category'] = data['word']

                    if 3 == data['column'][0]:
                        company['grade'] = data['word']

                    if 4 == data['column'][0]:
                        company['item'] = data['word']
                    company['area'] = '辽宁省'
            kk.append(company)
    for index, data in enumerate(kk):
        if not data['company']:
            kk[index]['company'] = kk[index - 1]['company']

    print(kk)
    Alldata = cerditdb.insert_many(kk)
    print(Alldata)


def trim(img, adderss):
    img2 = img.sum(axis=2)
    (row, col) = img2.shape
    tempr0 = 0
    tempr1 = 0
    tempc0 = 0
    tempc1 = 0
    # 765 是255+255+255,如果是黑色背景就是0+0+0，彩色的背景，将765替换成其他颜色的RGB之和，这个会有一点问题，因为三个和相同但颜色不一定同
    for r in range(0, row):
        if img2.sum(axis=1)[r] <= 730 * col:
            tempr0 = r
            break

    for r in range(row - 1, 0, -1):
        if img2.sum(axis=1)[r] <= 730 * col:
            tempr1 = r
            break

    for c in range(0, col):
        if img2.sum(axis=0)[c] <= 730 * row:
            tempc0 = c
            break

    for c in range(col - 1, 0, -1):
        if img2.sum(axis=0)[c] <= 730 * row:
            tempc1 = c
            break

    new_img = img[tempr0:tempr1 + 1, tempc0:tempc1 + 1, 0:3]
    io.imsave(adderss, new_img)
    # baiduOCR(address)


# baiduOCR('../staticImg/LiaoNing/5.jpg')
# MongoAD('16657913_1061387')
