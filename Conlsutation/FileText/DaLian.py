from aip import AipOcr
import json
import time
from pymongo import MongoClient

client = MongoClient('mongodb://admin:tongna888@106.12.113.52:27017/')
cerditdb = client.qualification.credit


def DaLianbaiduOCR(address):
    APP_ID = '16632496'
    API_KEY = 'iaY8a97WUgZifKMY3qvMbEmG'
    SECRECT_KEY = 'xbWyN2CKwBabjvUO1k7mACla7pziWDmN'
    client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)
    i = open(address, 'rb')
    img = i.read()
    message = client.tableRecognitionAsync(img)
    print(message)
    requestId = message['result'][0]['request_id']
    time.sleep(10)
    DaLianMongoAD(client, requestId)


def DaLianMongoAD(client, requestId):
    options = {"result_type": "json", "language_type": "CHN_ENG"}
    xx = client.getTableRecognitionResult(requestId, options)
    boyd = json.loads(xx['result']['result_data'])
    number = len(boyd['forms'][0]['body']) // 8
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
                        company['type'] = data['word']
                    if 3 == data['column'][0]:
                        company['grade'] = data['word']
                    if 4 == data['column'][0]:
                        company['category'] = data['word']
                    if 5 == data['column'][0]:
                        company['item'] = data['word']
                    if 7 == data['column'][0]:
                        company['result'] = data['word']
                    company['area'] = '辽宁省'
    #         kk.append(company)
    # print(kk)
    # Alldata = cerditdb.insert_many(kk)
    # print(Alldata)


DaLianbaiduOCR('../staticImg/DaLian/3.jpg')
