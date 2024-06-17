#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import re
from utils import Crawler
from config import CrawlerConfig

def format_cv(x):
    if isinstance(x, int):  
        return f"cv{x}"
    elif isinstance(x, str): 
        if x.startswith('cv') and x[2:].isdigit():  
            return f"{x}"
        elif x.isdigit():  
            return f"cv{x}"
        else:
            print(f"Invalid string format: {x}" )
            return ""
    else:
        print(f"Invalid input type: {type(x)}" )
        return ""

def extract_image_url(html_content):
    pattern = r'url\("?(.*?)(?:.avif)'    #匹配url("到.avif的字符
    urls = re.findall(pattern, html_content)
    return f"https:{urls[0]}.jpg" if urls else None

def extract_wh(text):
    pattern = r'@(\d+)w_(\d+)h'
    match = re.search(pattern, text)

    if match:
        width = match.group(1)
        height = match.group(2)
        return width, height
    else:
        return None, None

def get_meta(spider,url):
    r = spider.parser(url) 
    
    # date
    date_string = r.find(class_='publish-text').text
    # 解析为 datetime 对象
    date_obj = datetime.strptime(date_string, '%Y年%m月%d日 %H:%M')
    spider.date = date_obj.strftime('%Y-%m-%d')
    
    # post
    spider.post = str(r.find(class_='article-content'))
    spider.post = spider.post.replace('data-src', 'src')
    img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"]*)['"][^>]*>"""
    # img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"@]*)['"@][^>]*[>]"""    #匹配到@为止
    for idx,img in enumerate(re.findall(img_src, spider.post)):
        new_img=f"https:{img.replace('.avif','.jpg')}"
        new_img = spider.handle_img(new_img, *extract_wh(img))
        if idx == 0:
            spider.meta['header-img'] = new_img
        spider.post = spider.post.replace(img, new_img)
    spider.html2markdown()
    
    # meta
    spider.meta['title'] = r.find('h1', class_='title').text.strip()
    tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
    spider.meta['title'] = re.sub(tag, '', spider.meta['title'])
    spider.meta['author'] = r.find(class_='up-name').text.strip()
    spider.meta['original'] = url
    banner = str(r.find(class_='banner-container'))
    head_img = extract_image_url(banner)
    if head_img:
        spider.meta['header-img'] = spider.handle_img(head_img,*extract_wh(head_img))

def bilibili_spider(cfg):
    for id in cfg.ids:    
        id = format_cv(id)        
        if id == "":
            continue
        url = f'https://www.bilibili.com/read/{id}'
        spider = Crawler(cfg)
        get_meta(spider,url)
        spider.generator('bilibili')

if __name__ == '__main__':
    cfg = CrawlerConfig('config.json','bili')
    bilibili_spider(cfg)
