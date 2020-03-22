#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time
import re
from utils import parser
from utils import upload_img
from utils import html2markdown
from utils import generator
import sys


def get_meta(url):
    meta = {}
    r = parser(url)
    meta['title'] = r.find('h1', class_='title').text
    tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
    meta['title'] = re.sub(tag, '', meta['title'])
    meta['author'] = r.find(class_='up-name').text
    meta['original'] = url
    return meta

def get_date(url):
    date = parser(url).find(class_='create-time')['data-ts']
    date = time.localtime(int(date))
    date = time.strftime('%Y-%m-%d', date)
    return date

def get_posts(url):
    r = parser(url)
    post = str(r.find(class_='article-holder'))
    post = post.replace('data-src', 'src')
    img_src = r"""\bsrc\b\s*=\s*[\'\"]?([^\'\"]*)[\'\"]?"""
    for img in re.findall(img_src, post):
        new_img = upload_img(img)
        post = post.replace(img, new_img)
    post = html2markdown(post)
    return post

def bilibili_spider(id):
    url = f'https://www.bilibili.com/read/cv{id}'
    generator('bilibili', get_meta(url), get_posts(url), get_date(url))

if __name__ == '__main__':
    bilibili_spider(str(sys.argv[1]))
