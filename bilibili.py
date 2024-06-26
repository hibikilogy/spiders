#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import re
from utils import extract_wh_from
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

def extract_head_imgurl(html_content):
    pattern = r'url\("?(.*?)(?:.avif)'    #匹配url("到.avif的字符
    urls = re.findall(pattern, html_content)
    return f"https:{urls[0]}.jpg" if urls else None

def extract_wh_from_url(text):
    pattern = r'@(\d+)w_(\d+)h'
    match = re.search(pattern, text)

    if match:
        width = match.group(1)
        height = match.group(2)
        return width, height
    else:
        return None, None

def gen_down_url(url,w,h):
    if not (w and h):
        w,h = extract_wh_from_url(url)
    if w and h:
        down_url = f"{url.split('@')[0]}@{w}w_{h}h_.webp"
    else:
        down_url = url
    if not down_url.startswith('https:'):
        down_url = f"https:{down_url}"
    return down_url
            
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
    img_prtn = r"<img\s*[^>]*?>"  
    img_src = r'src\s*="([^"]*?)"'
    # img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"]*)['"][^>]*>"""
    # img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"@]*)['"@][^>]*[>]"""    #匹配到@为止
    for idx,img in enumerate(re.findall(img_prtn, spider.post)):
        img = img.replace('data-w="', 'width: ')
        img = img.replace('data-h="', 'height: ')
        for origin_img in re.findall(img_src, img)[::-1]:   #倒序
            w,h = extract_wh_from(img, 'style')
            down_url = gen_down_url(origin_img,w,h)
            ext = 'gif' if 'gif' in  down_url else 'jpg'
            new_img = spider.handle_img(down_url, w,h, ext)
            break
        if idx == 0:
            spider.meta['header-img'] = new_img
        spider.post = spider.post.replace(origin_img, new_img)
    
    spider.html2markdown()
    
    # meta
    spider.meta['title'] = r.find('h1', class_='title').text.strip()
    tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
    spider.meta['title'] = re.sub(tag, '', spider.meta['title'])
    spider.meta['author'] = r.find(class_='up-name').text.strip()
    spider.meta['original'] = url
    banner = str(r.find(class_='banner-container'))
    head_img = extract_head_imgurl(banner)
    if head_img:
        spider.meta['header-img'] = spider.handle_img(head_img,*extract_wh_from_url(head_img))

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
