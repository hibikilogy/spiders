#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
import html2text
import time
from tools import parser
from tools import upload_img
from tools import generator


def get_meta(url):
    meta = {}
    r = parser(url)
    meta['title'] = r.find('h1', class_='title').text
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
    post = html2text.html2text(post)
    return post

if __name__ == '__main__':
    url = 'https://www.bilibili.com/read/cv' + input('请输入文章 cv 号：')
    generator('bilibili', get_meta(url), get_posts(url), get_date(url))
