# -*- coding: utf-8 -*-
import scrapy
import re
import tomd

class TiebaSpider(scrapy.Spider):
    name = 'tieba'
    allowed_domains = ['tieba.baidu.com']
    start_urls = ['https://tieba.baidu.com/p/' + input('请输入帖子 ID：') + '?see_lz=1']

    def parse(self, response):
        meta = {}
        meta['url'] = response.url
        meta['title'] = response.css('.core_title_txt::text').get()
        meta['author'] = response.css('a.p_author_name::text').get()
        meta['date'] = response.css('.tail-info::text').getall()[1][:10]
        posts = response.css('.d_post_content').getall()
        content = ''
        for post in posts:
            post = re.sub('<div[^>]*>', '<p>', post)
            post = re.sub('<\/div[^>]*>', '</p>', post) 
            content += tomd.convert(post)
        with open(f'{meta["date"]}-{meta["title"]}.md', 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write('layout: post\n')
            f.write(f'title: {meta["title"]}\n')
            f.write(f'author: {meta["author"]}\n')
            f.write(f'original: {meta["url"]}\n')
            f.write(f'catalog: true\n')
            f.write('---\n')
            f.write(content)

