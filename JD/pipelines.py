# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

from openpyxl import Workbook
import requests


class JdPipeline(object):
    def __init__(self):
        self.wb1 = Workbook()
        self.wb2 = Workbook()
        self.ws1 = self.wb1.active
        self.ws2 = self.wb2.active
        self.ws1.append(['category', 'subclass'])  # title
        self.ws2.append(['subclass', 'item_id', 'name', 'img_url'])  # title

    def process_item(self, item, spider):
        # print(dict(item))
        # return item
        item = dict(item)
        if 'category' in item:
            self.ws1.append([item['category'], item['subclass']])
        elif 'name' in item:
            path = os.path.join(r'C:\Users\Admin\ScrapyProjects\JD\result', item['subclass'])
            if not os.path.isdir(path):
                os.makedirs(path)
            with open(os.path.join(path, item['item_id']) + '.png', 'wb') as f:
                response = requests.get('http:' + item['img_url'])
                f.write(response.content)
            self.ws2.append([item['subclass'], item['item_id'], item['name'], item['img_url']])
        return item

    def close_spider(self, spider):
        self.wb1.save(r'C:\Users\Admin\ScrapyProjects\JD\result\category.xlsx')
        self.wb2.save(r'C:\Users\Admin\ScrapyProjects\JD\result\item.xlsx')
