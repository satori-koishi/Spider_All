import requests
import ssl
from aip import AipOcr
import json
import time


def baiduOCR():
    """利用百度api识别文本，并保存提取的文字
    picfile:    图片文件名
    outfile:    输出文件
    """

    APP_ID = '16632496'
    API_KEY = 'iaY8a97WUgZifKMY3qvMbEmG'
    SECRECT_KEY = 'xbWyN2CKwBabjvUO1k7mACla7pziWDmN'
    client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)
    #
    i = open('./staticImg/test/xx.jpg', 'rb')
    img = i.read()
    message = client.tableRecognitionAsync(img)
    print(message)
    # print(message)
    requestId = message['result'][0]['request_id']
    print(requestId)
    time.sleep(15)
    MongoAD(client, requestId)

    # """ 调用表格识别结果 """
    #
    # """ 如果有可选参数 """


def MongoAD(client, requestId):
    options = {"result_type": "json", "language_type": "CHN_ENG"}
    #
    # """ 带参数调用表格识别结果 """
    xx = client.getTableRecognitionResult(requestId, options)
    print(xx)
    boyd = json.loads(xx['result']['result_data'])
    print(len(boyd['forms'][0]['body']))
    Hang = (len(boyd['forms'][0]['body']) // 5) - 1
    print(Hang)
    for index, data in enumerate(boyd['forms'][0]['body']):
        print(index)
        if index == Hang + 1:
            break
        if index:
            print('多少行-%s---单位名称-%s---类型-%s---级别-%s---专业（专项）-%s' % (
                data['word'], boyd['forms'][0]['body'][(Hang * 1) + index + 1]['word'],
                boyd['forms'][0]['body'][(Hang * 2) + index + 2]['word'],
                boyd['forms'][0]['body'][(Hang * 3) + index + 3]['word'],
                boyd['forms'][0]['body'][(Hang * 4) + index + 4]['word'])
                  )


baiduOCR()
