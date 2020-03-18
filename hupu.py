#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import html2text
from utils import parser
from utils import upload_img
from utils import generator


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
    for img in re.findall(img_src, post):
        try:
            i = img.index('?')
            img = img[:i]
        except ValueError:
            pass
        new_img = upload_img(img)
        post = post.replace(img, new_img)
    post = html2text.html2text(post)
    return post

if __name__ == '__main__':
    url = 'https://bbs.hupu.com/' + input('请输入帖子 ID：') + '.html'
    generator('虎扑', get_meta(url), get_posts(url), get_date(url))
