#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import html2text
from utils import parser
from utils import upload_img
from utils import generator
import sys


def get_meta(url):
    meta = {}
    r = parser(url)
    meta['title'] = r.find('h1', id='j_data').text
    meta['author'] = r.find('a', class_='u').text
    meta['original'] = url
    return meta

def get_date(url):
    date = parser(url).find(class_='stime').text[:10]
    return date

def get_posts(url):
    r = parser(url)
    post = str(r.find(class_='quote-content'))
    img_src = r"""\bsrc\b\s*=\s*[\'\"]?([^\'\"]*)[\'\"]?"""
    post = post.replace('data-original', 'src')
    place_holder = 'https://b1.hoopchina.com.cn/web/sns/bbs/images/placeholder.png'
    for img in re.findall(img_src, post):
        if img == place_holder:  # 懒加载
            post = post.replace(f'src="{place_holder}"', '')
            continue
        try:
            i = img.index('?')
            img_real = img[:i]
        except ValueError:
            img_real = img
        new_img = upload_img(img_real)
        post = post.replace(img, new_img)
    post = html2text.html2text(post)
    return post

def hupu_spider(id):
    url = f'https://bbs.hupu.com/{id}.html'
    generator('虎扑', get_meta(url), get_posts(url), get_date(url))

if __name__ == '__main__':
    hupu_spider(sys.argv[1])
