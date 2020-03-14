# -*- coding: utf-8 -*-
import scrapy


class HupuSpider(scrapy.Spider):
    name = 'hupu'
    allowed_domains = ['bbs.hupu.com']
    start_urls = ['http://bbs.hupu.com/']

    def parse(self, response):
        pass
