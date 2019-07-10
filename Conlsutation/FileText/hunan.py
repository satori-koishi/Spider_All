from aip import AipOcr
import json
import time
from pymongo import MongoClient

APP_ID = '16657913'
API_KEY = 'SNbBvp0R4Lbu6DqssoTnUGc0'
SECRECT_KEY = 'hp4tO0XDGDSFZ5tLbSbV68qgDvn4fENL'
client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)


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
    print(len(boyd['forms'][0]['body']))
    print(number, '行数')
    kk = []
    for i in range(number):
        if i:
            company = {}
            for data in boyd['forms'][0]['body']:
                if data['row'][0] == i:
                    if 1 == data['column'][0]:
                        company['company'] = data['word']

                    if 2 == data['column'][0]:
                        company['category'] = data['word']

                    if 3 == data['column'][0]:
                        company['grade'] = data['word']

                    if 4 == data['column'][0]:
                        company['item'] = data['word']
                    company['area'] = '湖南省'
            kk.append(company)
    print(kk)
    # Alldata = cerditdb.insert_many(kk)
    # print(Alldata)


baiduOCR('../staticImg/HuNan/5.png')
# MongoAD('16657913_1064265')
