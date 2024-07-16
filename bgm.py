
# -*- coding: utf-8 -*-
import re
# from selenium.webdriver.common.by import By
from utils import extract_wh_from
from config import CrawlerConfig
from utils import Crawler

DOM_BGM={
    "date": ['div', 're_info'],
    "content": ['div', 'blog_entry'],
    "title": ['h1', ''],
    "author": ['a', 'avatar l'],
    "img": ["xpath", "//img[contains(@class, 'code')]"]
    }

def id_check(id):
    return id != "" and (isinstance(id, int) or id.isdigit())


def get_meta(spider,url):
    
    r = spider.parser(url) 
    cDOM = DOM_BGM 

    # date
    date_string = r.find(cDOM["date"][0], class_=cDOM["date"][1]).text
    spider.meta['date'] = date_string.split()[0]
    
    # post
    post_content = r.find(cDOM["content"][0], class_=cDOM["content"][1])
    spider.post = str(post_content)
    
    def trans_img_url(elem,url):
        w,h = extract_wh_from(elem,'elem')
        return spider.download_img(url, w,h)

    
    # spider.driver.fullscreen_window()
    for idx,img in enumerate(spider.driver.find_elements(cDOM["img"][0],cDOM["img"][1])):

        origin_img = img.get_attribute("src")

        if origin_img:
            new_img = trans_img_url(img, origin_img)
            spider.post = spider.post.replace(origin_img, new_img)
            if idx == 0:
                spider.meta['header-img'] = new_img
    
    spider.html2markdown()
    
    # meta
    title_item = r.find(cDOM["title"][0], class_=cDOM["title"][1])
    if title_item:
        spider.meta['title'] = title_item.text
        span_text = title_item.find('span').text
        spider.meta['title'] = spider.meta['title'].replace(span_text,'').strip()
        tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
        spider.meta['title'] = re.sub(tag, '', spider.meta['title'])
    spider.meta['author'] = r.find(cDOM["author"][0], class_=cDOM["author"][1]).text.strip()
    spider.meta['original'] = url
    banner = str(r.find(class_='banner-image'))


def bgm_spider(cfg):
    for idx, id in enumerate(cfg.ids):   
        if not id_check(id):
            continue
        url = f'https://bgm.tv/blog/{id}'

        spider = Crawler(cfg)
        get_meta(spider,url)
        custom_fname = cfg.fname[idx] if idx < len(cfg.fname) else ''
        spider.generator('bangumi', custom_fname)

if __name__ == '__main__':
    cfg = CrawlerConfig('config.json','bgm')
    bgm_spider(cfg)
