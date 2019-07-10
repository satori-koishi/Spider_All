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
    kk = {}
    for index in boyd['forms'][0]['body']:
        try:
            kk[index['row'][0]].append(index['word'])
        except KeyError:
            kk[index['row'][0]] = []
            kk[index['row'][0]].append(index['word'])
    xx = []
    for index, data in kk.items():
        dd = {}
        if index:
            dd['company'] = data[2]
            dd['area'] = '辽宁省'
            dd['category'] = data[2]
            dd['item'] = data[6]
            dd['grade'] = data[1]
            dd['type'] = data[3]
            dd['result'] = data[2]
        xx.append(dd)
    print(xx)
