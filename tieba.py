#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from utils import parser
from utils import upload_img
from utils import html2markdown
from config import CrawlerConfig
from utils import Crawler

def id_check(id):
    return id != "" and (isinstance(id, int) or id.isdigit())
     

def get_posts(url):
    def get_post(page_url):
        return parser(page_url).find_all(class_='d_post_content')
    page = parser(url).find_all('li', class_='l_reply_num')[0].find_all('span')[1].text
    posts = []
    for i in range(1, int(page) + 1):
        posts += [x for x in get_post(url + '&pn=' + str(i))]
    content = ''
    img_src = r"""\bsrc\b\s*=\s*[\'\"]?([^\'\"]*)[\'\"]?""" 
    for post in posts:
        post = str(post)
        post = re.sub('<div[^>]*>', '<p>', post)
        post = re.sub('</div[^>]*>', '</p>', post)
        # upload img
        # TODO: 改为保存到本地
        for img in re.findall(img_src, post):
            new_img = upload_img(img)
            post = post.replace(img, new_img)
        content += html2markdown(post)
    return content


def get_meta(spider,url):
    if spider.cfg.static:
        r = spider.static_parser(url)
    else:
        r = spider.dynamic_parser(url) #头图为动态渲染
    
    # date
    date_string = r.find_all(class_='tail-info')[3].text[:10]
    spider.date = date_string
    
    # post
    spider.post = get_posts(url)
    spider.html2markdown()
    
    # meta
    spider.meta['title'] = r.find(class_='core_title_txt').text.strip()
    tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
    spider.meta['title'] = re.sub(tag, '', spider.meta['title'])
    spider.meta['author'] = r.find('a', class_='p_author_name').text.strip()
    spider.meta['original'] = url

def tieba_spider(cfg):
    for id in cfg.ids:          
        if not id_check(id):
            continue
        url = f'https://tieba.baidu.com/p/{id}?see_lz=1'

        spider = Crawler(cfg)
        get_meta(spider,url)
        spider.generator('贴吧')

if __name__ == '__main__':
    cfg = CrawlerConfig('config.json')
    tieba_spider(cfg)
