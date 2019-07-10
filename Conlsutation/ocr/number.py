import pytesseract
from PIL import Image

# # str_number = pytesseract.image_to_data(image, lang='chi_sim')
# # print(str_number, dir(str_number))
# def erzhihua(image, threshold):
#     ''':type image:Image.Image'''
#     image = image.convert('L')
#     table = []
#     for i in range(256):
#         if i < threshold:
#             table.append(0)
#         else:
#             table.append(1)
#     return image.point(table, '1')
#
#
# im = Image.open("./img/2.jpg")
# image = erzhihua(im, 180)
# image.show()
# image.save('./img/test.jpg')
# result = pytesseract.image_to_string(image, lang='chi_sim')
# print(result)
#
# im = Image.open("./img/7.jpg")
# result = pytesseract.image_to_string(im, lang='tongna')
# print(result)

import requests
import json

data = {'creditType': 'creditType', 'keyWord': '中北交通', 'captcha': '6'}
head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/74.0.3729.108 Safari/537.36'}
xx = requests.post(url='http://www.sxcredit.gov.cn/queryCreditData.jspx', data=json.dumps(data), headers=head)
print(xx.text)
