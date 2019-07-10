# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
from openpyxl import Workbook
import json
import csv
class ZizhisearchPipeline(object):
    def __init__(self):
        self.workbook = Workbook()
        self.ws = self.workbook.active
        self.ws.append(['企业名称', '统一社会信用代码/注册号', '法定代表人', '注册属地'])  # 设置表头
        # self.file = codecs.open('lagou2.json', 'w', encoding='utf-8'
    def process_item(self, item, spider):
        line = [item['Enterprise_name'], item['Registration_number'], item['Legal_representative'], item['Registered_place']]  # 把数据中每一项整理出来
        self.ws.append(line)
        self.workbook.save('lagou2.csv')  # 保存xlsx文件
        # line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        # self.file.write(line)
        print('添加成功')
        return item
    def spider_closed(self, spider):
        # self.file.close()
        pass
class ZizhisearchPipelin_see_data(object):
    def process_item(self, item, spider):
        print('企业名称-%s__ 统一社会信用代码/注册号-%s__ 法定代表人-%s__ 注册属地%s'%
              (item['Enterprise_name'],item['Registration_number'],item['Legal_representative'],
               item['Registered_place']))
        return item



