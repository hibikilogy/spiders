# -*- coding: utf-8 -*-
import scrapy


class NgaSpider(scrapy.Spider):
    name = 'nga'
    allowed_domains = ['bbs.nga.cn']
    start_urls = ['http://bbs.nga.cn/']

    def parse(self, response):
        pass
