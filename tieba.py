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
     
def extract_wh(text):
    pattern = r'width="(\d+)".*?height="(\d+)"|height="(\d+)".*?width="(\d+)"'
    match = re.search(pattern, text)

    if match:
        # 由于正则表达式中有多个捕获组，需要检查哪个捕获组匹配到了值
        if match.group(1) and match.group(2):
            width = match.group(1)
            height = match.group(2)
        elif match.group(3) and match.group(4):
            width = match.group(4)
            height = match.group(3)
        return width, height
    else:
        return None, None


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
            date_string = r.find_all(class_='tail-info')[3].text[:10]
            spider.date = date_string
            # meta
            spider.meta['title'] = r.find(class_='core_title_txt').text.strip()
            tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
            spider.meta['title'] = re.sub(tag, '', spider.meta['title'])
            spider.meta['author'] = r.find('a', class_='p_author_name').text.strip()
            spider.meta['original'] = url
        i+=1
        posts += [str(x) for x in r.find_all(class_='d_post_content')]
    
    img_prtn = r"""<img\s*[^>]*?>"""   
    img_src = r'src\s*="([^"]*?)"'
    spider.post = ''
    for i,post in enumerate(posts):
        post = re.sub('<div[^>]*>', '<p>', post)
        post = re.sub('</div[^>]*>', '</p>', post)
        # upload img
        for j,img in enumerate(re.findall(img_prtn, post)):
            for origin_img in re.findall(img_src, img):
                new_img = spider.handle_img(origin_img, *extract_wh(img))
            if i+j == 0:
                spider.meta['header-img'] = new_img
            post = post.replace(origin_img, new_img)
            ...
        spider.post += post
    spider.html2markdown()


def tieba_spider(cfg):
    for id in cfg.ids:          
        if not id_check(id):
            continue
        url = f'https://tieba.baidu.com/p/{id}?see_lz=1'

        spider = Crawler(cfg)
        get_meta(spider,url)
        spider.generator('贴吧')

if __name__ == '__main__':
    cfg = CrawlerConfig('config.json','tieba')
    tieba_spider(cfg)
