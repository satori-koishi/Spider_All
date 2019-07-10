from aip import AipOcr
import json
import time
from Tool.DeBlanking import trim
from Tool.TableDisdinguish import baiduOCR
from skimage import io
import sys
from pymongo import MongoClient

client = MongoClient('mongodb://admin:tongna888@106.12.113.52:27017/')
cerditdb = client.qualification.credit


# cc = cerditdb.insert_many(wqe)
# print(cc)
