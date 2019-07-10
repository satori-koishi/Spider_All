import redis

pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
r = redis.Redis(connection_pool=pool)

number = r.scard('NonExistentWaterCompany') + r.scard('OkWaterCompany')
print(r.scard('NonExistentWaterCompany'), '没有基本信息的')
print(r.scard('OkWaterCompany'), '存在基本信息的')
print(number, '总计')
print('原数据共16197条')
lose = 16197 - number
print(lose, '丢失数据--或重复')
print('-------------------------------水利-------------------------------')
# import scrapy
# import redis
# from scrapy import Selector
# from scrapy.http import Request
# import time
# import random
# import json
# import re


