#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from utils import extract_wh_from
from config import CrawlerConfig
from utils import Crawler

def id_check(id):
    return id != "" and (isinstance(id, int) or id.isdigit())


def get_meta(spider,url):
    # 首先获取页数
    page = 1
    i = 1
    posts = []
    while i <= page:
        r = spider.parser(f'{url}&pn={i}')  #当前页
        if posts == []:
            page = int(r.find_all('li', class_='l_reply_num')[0].find_all('span')[1].text)
            # date
            date_string = r.find_all(class_='tail-info')[-1].text[:10]
            spider.date = date_string
            # meta
            spider.meta['title'] = r.find(class_='core_title_txt').text.strip()
            tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
            spider.meta['title'] = re.sub(tag, '', spider.meta['title'])
            spider.meta['author'] = r.find('a', class_='p_author_name').text.strip()
            spider.meta['original'] = url
        i+=1
        posts += [str(x) for x in r.find_all(class_='d_post_content')]
    
    def trans_img_url(container,url):
        w,h = extract_wh_from(container,'attr')
        return spider.handle_img(url, w,h)
    img_prtn = r"<img\s*[^>]*?>"  
    img_src = r'src\s*="([^"]*?)"'
    spider.post = ''
    for i,post in enumerate(posts):
        post = re.sub('<div[^>]*>', '<p>', post)
        post = re.sub('</div[^>]*>', '</p>', post)
        # upload img
        for j,img in enumerate(re.findall(img_prtn, post)):
            for origin_img in re.findall(img_src, img):
                if origin_img == "": continue
                new_img = trans_img_url(img, origin_img)
            if i+j == 0:
                spider.meta['header-img'] = new_img
            post = post.replace(origin_img, new_img)
            ...
        spider.post += post
    spider.html2markdown()


def tieba_spider(cfg):
    for idx, id in enumerate(cfg.ids):   
        if not id_check(id):
            continue
        url = f'https://tieba.baidu.com/p/{id}?see_lz=1'

        spider = Crawler(cfg)
        get_meta(spider,url)
        custom_fname = cfg.fname[idx] if idx < len(cfg.fname) else ''
        spider.generator('贴吧', custom_fname)

if __name__ == '__main__':
    cfg = CrawlerConfig('config.json','tieba')
    tieba_spider(cfg)
