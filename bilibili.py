#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import re
from utils import extract_wh
from utils import Crawler
from config import CrawlerConfig

DOM_DYN={
    "date": ['div', 'opus-module-author__pub__text'],
    "content": ['div', 'opus-module-content'],
    "title": ['span', 'opus-module-title__text'],
    "author": ['div', 'opus-module-author__name'],
}
DOM_CV={
    "date": ['span', 'publish-text'],
    "content": ['div', 'article-content'],
    "title": ['h1', 'title'],
    "author": ['a', 'up-name'],
}

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
    if w or h:
        down_url = f"{url.split('@')[0]}@{f'{w}w_' if w else ''}{f'{h}h_' if h else ''}.webp"
    else:
        down_url = url
    if not down_url.startswith('https:'):
        down_url = f"https:{down_url}"
    return down_url, w, h
            
def get_meta(spider,url):
    def trans_img_url(container,url):
        w,h = extract_wh(container)
        down_url,w,h = gen_down_url(url,w,h)
        return spider.handle_img(down_url, w,h)
    r = spider.parser(url) 
    opus_top = ''
    if spider.cfg.is_dyn: 
        opus_top = r.find('div', class_='opus-module-top')
        opus_top = str(opus_top) if opus_top else ''
        cDOM = DOM_DYN 
    else:
        cDOM = DOM_CV
    # date
    date_string = r.find(cDOM["date"][0], class_=cDOM["date"][1]).text
    # 解析为 datetime 对象
    date_obj = datetime.strptime(date_string, '%Y年%m月%d日 %H:%M')
    spider.date = date_obj.strftime('%Y-%m-%d')
    
    # post
    post_content = r.find(cDOM["content"][0], class_=cDOM["content"][1])
    spider.post = str(post_content) + opus_top
    spider.post = spider.post.replace('data-src', 'src')
    
    img_prtn = r"<img\s*[^>]*?>"  
    img_src = r'src\s*="([^"]*?)"'
    handled = []
    if spider.cfg.is_dyn:
        for idx,img in enumerate(post_content.find_all('div', class_='b-img')):
            img = str(img)
            for origin_img in re.findall(img_src, img):
                if origin_img == "": continue
                new_img = trans_img_url(img, origin_img)
                break
            if idx == 0:
                spider.meta['header-img'] = new_img
            if origin_img:
                spider.post = spider.post.replace(origin_img, new_img)
            handled.append(new_img)

    # img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"]*)['"][^>]*>"""
    # img_src = r"""<img\b[^>]*\bsrc\s*=\s*['"]([^'"@]*)['"@][^>]*[>]"""    #匹配到@为止
    for idx,img in enumerate(re.findall(img_prtn, spider.post)):
        skip = False
        img = img.replace('data-w="', 'width: ')
        img = img.replace('data-h="', 'height: ')
        for origin_img in re.findall(img_src, img)[::-1]:   #倒序
            if origin_img == "": continue
            if origin_img in handled: 
                skip = True
                continue
            new_img = trans_img_url(img, origin_img)
            break
        if idx == 0 and len(handled)==0:
            spider.meta['header-img'] = new_img
        if not skip and origin_img:
            spider.post = spider.post.replace(origin_img, new_img)
    
    spider.html2markdown()
    
    # meta
    title_item = r.find(cDOM["title"][0], class_=cDOM["title"][1])
    if title_item:
        spider.meta['title'] = title_item.text.strip()
        tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
        spider.meta['title'] = re.sub(tag, '', spider.meta['title'])
    spider.meta['author'] = r.find(cDOM["author"][0], class_=cDOM["author"][1]).text.strip()
    spider.meta['original'] = url
    banner = str(r.find(class_='banner-image'))
    head_img = extract_head_imgurl(banner)
    if head_img:
        spider.meta['header-img'] = trans_img_url(banner, head_img)

def bilibili_spider(cfg):
    for idx, id in enumerate(cfg.ids):    
        if cfg.is_dyn:
            url = f'https://www.bilibili.com/opus/{id}'
        else:
            id = format_cv(id)        
            url = f'https://www.bilibili.com/read/{id}'
        if id == "":
            continue
        spider = Crawler(cfg)
        get_meta(spider,url)
        custom_fname = cfg.fname[idx] if idx < len(cfg.fname) else ''
        spider.generator('bilibili', custom_fname)

if __name__ == '__main__':
    cfg = CrawlerConfig('config.json','bili')
    bilibili_spider(cfg)
