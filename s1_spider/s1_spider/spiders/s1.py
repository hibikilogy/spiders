# -*- coding: utf-8 -*-
import scrapy


class S1Spider(scrapy.Spider):
    name = 's1'
    allowed_domains = ['bbs.saraba1st.com']
    start_urls = ['http://bbs.saraba1st.com/']

    def parse(self, response):
        pass
