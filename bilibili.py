#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import re
from utils import Crawler
from utils import html2markdown
import sys


def extract_image_url(html_content):
    pattern = r'url\("?(.*?)(?:@|$)'    #匹配url("到@的字符
    urls = re.findall(pattern, html_content)
    return f"https:{urls[0]}" if urls else None

def get_meta(spider):
    # date
    date_string = r.find(class_='publish-text').text
    # 解析为 datetime 对象
    date_obj = datetime.strptime(date_string, '%Y年%m月%d日 %H:%M')
    date = date_obj.strftime('%Y-%m-%d')
    
    # meta
    meta = {}
    r = spider.dynamic_parser(r'E:\software\common\webBrowser\chrome\chromedriver.exe') #头图为动态渲染
    # r = spider.static_parser()  
    meta['title'] = r.find('h1', class_='title').text.strip()
    tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
    meta['title'] = re.sub(tag, '', meta['title'])
    meta['author'] = r.find(class_='up-name').text.strip()
    meta['original'] = spider.url
    banner = str(r.find(class_='banner-container'))
    head_img = extract_image_url(banner)
    if head_img:
        meta['header-img'] = head_img
        # meta['header-img'] = spider.upload_img(head_img,date)   #直接使用原图床则注释此行
    
    # post
    post = str(r.find(class_='article-content'))
    post = post.replace('data-src', 'src')
    img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"]*)['"][^>]*>"""
    # img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"@]*)['"@][^>]*[>]"""    #匹配到@为止
    for img in re.findall(img_src, post):
        new_img=f"https:{img.split('@')[0]}"
        # new_img = spider.upload_img(new_img,date)   #直接使用原图床则注释此行
        post = post.replace(img, new_img)
    post = html2markdown(post)
    return meta,date,post

def bilibili_spider(ids):
    for id in ids:
        if id == '':
            continue
        url = f'https://www.bilibili.com/read/cv{id}'
        spider = Crawler(url)
        spider.generator('bilibili', *get_meta(spider))

if __name__ == '__main__':
    bilibili_spider(sys.argv[1:])
