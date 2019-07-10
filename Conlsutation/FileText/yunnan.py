from aip import AipOcr
import json
import time
from pymongo import MongoClient

client = MongoClient('mongodb://admin:tongna888@106.12.113.52:27017/')
cerditdb = client.qualification.credit


def baiduOCR(address):
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
    MongoAD(client, requestId)


def MongoAD(client, requestId):
    options = {"result_type": "json", "language_type": "CHN_ENG"}
    xx = client.getTableRecognitionResult(requestId, options)
    boyd = json.loads(xx['result']['result_data'])
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
                        company['type'] = data['word']
                    if 3 == data['column'][0]:
                        company['grade'] = data['word']
                    if 4 == data['column'][0]:
                        company['item'] = data['word']
                    company['area'] = '云南省'
            kk.append(company)
    Alldata = cerditdb.insert_many(kk)
    print(Alldata)


for i in range(1, 9):
    baiduOCR('../staticImg/YunNan/%s.png' % i)
