# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import quote, unquote
from JD.items import JdItem, CatItem
import os


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com']
    categories = {
        '休闲零食': '2200962565',
        '水饮冲调':'2200962579',
        '粮油调味':'2200962577',
        '中外名酒':'2200962567',
        '进口食品':'2200962566',
        '纸品湿巾':'2200962748',
        '个人护理':'2200962580',
        '生活电器':'2200962563',
        '家居日用':'2200962569',
        '家庭清洁':'2200962751',
        '衣物清洁':'2200962750',
        '新鲜水果':'2200962573',
    }
    base_url_1 = 'https://api.m.jd.com/client.action?functionId=getTrackBabelAdvert&body=%7B%22advertId%22%3A%'
    base_url_2 = '%22%2C%22moduleId%22%3A18796127%2C%22activityId%22%3A%2200381161%22%2C%22pageId%22%3A%22990893%22%2C%22transParam%22%3A%22%7B%5C%22bsessionId%5C%22%3A%5C%221115d9d3-39ae-4cc0-a825-2af9c49e2d9f%5C%22%2C%5C%22babelChannel%5C%22%3A%5C%22%5C%22%2C%5C%22actId%5C%22%3A%5C%2200381161%5C%22%2C%5C%22enActId%5C%22%3A%5C%222rUzGMirroT1PbGPjrc5sckJjrju%5C%22%2C%5C%22pageId%5C%22%3A%5C%22990893%5C%22%2C%5C%22encryptCouponFlag%5C%22%3A%5C%221%5C%22%2C%5C%22requestChannel%5C%22%3A%5C%22h5%5C%22%7D%22%2C%22secCatTransParam%22%3A%22%22%2C%22resType%22%3A%22%22%2C%22mitemAddrId%22%3A%22%22%2C%22geo%22%3A%7B%22lng%22%3A%22%22%2C%22lat%22%3A%22%22%7D%2C%22addressId%22%3A%22%22%2C%22posLng%22%3A%22%22%2C%22posLat%22%3A%22%22%2C%22focus%22%3A%22%22%2C%22innerAnchor%22%3A%22%22%2C%22cv%22%3A%222.0%22%7D&screen=750*1334&client=wh5&clientVersion=1.0.0&sid=&uuid=15978604453521585399959&area='

    # start_urls = ['http://'jd.com'/']

    def start_requests(self):
        if not os.path.isdir(r'C:\Users\Admin\ScrapyProjects\JD\result'):
            os.makedirs(r'C:\Users\Admin\ScrapyProjects\JD\result')
        for cat in self.categories:
            url = self.base_url_1 + self.categories[cat] + self.base_url_2
            yield scrapy.Request(url, callback=self.subclass_parse)

    def subclass_parse(self, response):
        ### get the category name from above, to save in excel later
        request_url = response.request.url
        cat_id = request_url[len(self.base_url_1):(len(request_url) - len(self.base_url_2))]
        for k, v in self.categories.items():
            if v == cat_id:
                category = k
                # print(category)
        ###

        subclass_list = json.loads(response.text)['list']
        ### test
        # url = 'https://so.m.jd.com/ware/search.action?keyword=' + quote(subclass_list[0]['jump']['params']['keyWord'])
        ###
        for subclass in subclass_list:
            # print(subclass['jump']['params']['keyWord'])
            # print(subclass['name'])
            item = CatItem()
            item['category'] = category
            item['subclass'] = subclass['name']
            yield item
            keyword = subclass['jump']['params']['keyWord']
            url = 'https://so.m.jd.com/ware/search.action?keyword=' + quote(keyword)
            # print(url)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # print(response.text)
        itemList = response.xpath('//div[@class="search_prolist_item"]')
        subclass = response.xpath('//title/text()').extract()[0].split(' ')[0]
        for node in itemList[0:4]:  # only the info of the first 4 items can be retrieved
            item = JdItem()
            # xpath returns a list
            # .// means any child node under current node
            item['name'] = node.xpath('.//div[@class="search_prolist_title"]/text()').extract()[0].strip()
            item['img_url'] = node.xpath('.//div[@class="search_prolist_cover"]/img[@class="photo"]/@src').extract()[0]
            item['subclass'] = subclass
            item['item_id'] = node.xpath('./@skuid').extract()[0]
            yield item  # certain subclass can not be retrieved, need to clean in pipeline
