# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# class xiaohuaPipeline(object):
#     def __init__(self,*args,**kwargs):
#             self.f = open('xiaohua.json', 'a')
#     def open_spider(self,spider):
#         pass
#     def close_spider(self,spider):
#         pass
#     def process_item(self, item, spider):
#         pass


import redis


class ShanxiJianzhuPipeline(object):

    def open_spider(self, spider):
        print('打开spider')
        self.province_name = spider.name
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        title_name1 = self.r.scard('title_name1')
        title_name3 = self.r.scard('title_name3')
        self.f = open('/home/www/spider_rizhi/work_data', 'a', encoding='utf-8')
        self.f.write(self.province_name + '\n' + '\t当前redis-title_name1的数据为---%s\n'
                                                 '\t当前redis-title_name3的数据为--%s\n'
                     % (title_name1, title_name3))

    def close_spider(self, spider):
        title_name1 = self.r.scard('title_name1')
        title_name3 = self.r.scard('title_name3')
        print('关闭spider')
        self.f.write('\t\t---%s次省份数据添加完成--title_name1的数据为'
                     '%s---title_name3的数据为%s\n\n'
                     % (self.province_name, title_name1, title_name3))

    def process_item(self, item, spider):
        pass
