# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime

class ZizhinamePipeline(object):
    def __init__(self, *args, **kwargs):
        new_time_error = datetime.datetime.now()
        new_zz = str(new_time_error)
        self.f = new_zz.split('.')[0]
        self.f = self.f.replace(' ', '')
        self.f = self.f.replace('-', '')
        self.f = self.f.replace(':', '')
        self.f = self.f + '.txt'
        self.z = open(self.f, 'a+', encoding="utf-8")
    def process_item(self, item, spider):
        # print(item['name'], '此公司已经添加到了')
        company_name = item['name']
        self.z.write(company_name+'\n',)
        return item

    # def open_spider(self, spider):
    def spider_closed(self, spider):
        self.f.close()

