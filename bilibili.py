#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import re
from utils import Crawler
from utils import html2markdown
from config import CrawlerConfig


def extract_image_url(html_content):
    pattern = r'url\("?(.*?)(?:@|$)'    #匹配url("到@的字符
    urls = re.findall(pattern, html_content)
    return f"https:{urls[0]}" if urls else None

def get_meta(spider,url):
    if 'static' in  spider.cfg.args and spider.cfg.args.static:
        r = spider.static_parser(url)
    else:
        r = spider.dynamic_parser(url) #头图为动态渲染
    
    # date
    date_string = r.find(class_='publish-text').text
    # 解析为 datetime 对象
    date_obj = datetime.strptime(date_string, '%Y年%m月%d日 %H:%M')
    date = date_obj.strftime('%Y-%m-%d')

    # meta
    meta = {}
    
    # post
    post = str(r.find(class_='article-content'))
    post = post.replace('data-src', 'src')
    img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"]*)['"][^>]*>"""
    # img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"@]*)['"@][^>]*[>]"""    #匹配到@为止
    for idx,img in enumerate(re.findall(img_src, post)):
        new_img=f"https:{img.split('@')[0]}"
        new_img = spider.upload_img(new_img,date)
        if idx == 0:
            meta['header-img'] = new_img
        post = post.replace(img, new_img)
    post = html2markdown(post)
    
    # meta
    meta['title'] = r.find('h1', class_='title').text.strip()
    tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
    meta['title'] = re.sub(tag, '', meta['title'])
    meta['author'] = r.find(class_='up-name').text.strip()
    meta['original'] = url
    banner = str(r.find(class_='banner-container'))
    head_img = extract_image_url(banner)
    if head_img:
        meta['header-img'] = spider.upload_img(head_img,date)
    
    return meta,date,post

def bilibili_spider(cfg):
    for id in cfg.ids:
        if id == '':
            continue
        url = f'https://www.bilibili.com/read/cv{id}'
        spider = Crawler(cfg)
        spider.generator('bilibili', *get_meta(spider,url))

if __name__ == '__main__':
    cfg = CrawlerConfig()
    cfg.parse_args()
    bilibili_spider(cfg)
