# -*- coding: utf-8 -*-
import scrapy
import re
import html2text
from tieba_spider.items import TiebaSpiderItem

class TiebaSpider(scrapy.Spider):
    name = 'tieba'
    allowed_domains = ['tieba.baidu.com']
    start_urls = ['https://tieba.baidu.com/p/' + input('请输入帖子 ID：') + '?see_lz=1']

    def parse(self, response):
        item = TiebaSpiderItem()
        item['url'] = response.url
        item['title'] = response.css('.core_title_txt::text').get()
        item['author'] = response.css('a.p_author_name::text').get()
        item['date'] = response.css('.tail-info::text').getall()[1][:10]
        item['content'] = ''
        posts = response.css('.d_post_content').getall()
        for post in posts:
            post = re.sub('<div[^>]*>', '<p>', post)
            post = re.sub('<\/div[^>]*>', '</p>', post) 
            item['content'] += html2text.html2text(post)
        next_page = response.xpath('//a[@class="next pagination-item "]/@href')
        if next_page:
            pass
        yield item
