#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import html2text
from utils import parser
from utils import upload_img
from utils import generator
import sys


def lz_only(url):
    suffix = parser(url).find_all(class_='authi')[1].find('a')['href']
    return f'https://bbs.saraba1st.com/2b/{suffix}'

def get_posts(url):
    def get_post(page_url):
        return parser(page_url).find_all(class_='t_fsz')
    # page = parser(url).find(id='fj').find('input')['size']
    posts = []
    # for i in range(1, int(page) + 1):
    #    posts += [x for x in get_post(url[:-8] + str(i) + '-1.html')]
    content = ''
    posts = get_post(url)
    img_src = r"""\bsrc\b\s*=\s*[\'\"]?([^\'\"]*)[\'\"]?""" 
    for post in posts:
        try:
            post.find(class_='pstatus').clear()  # 移除 本贴最后……
            post.find(class_='tip').clear()  # 移除 附件：……
        except AttributeError:
            pass
        post = str(post)
        post = re.sub('<div[^>]*>', '<p>', post)
        post = re.sub('<\/div[^>]*>', '</p>', post)
        for img in re.findall(img_src, post):
            new_img = upload_img(img)
            post = post.replace(img, new_img)
        content += html2text.html2text(post)
    return content

def get_meta(url):
    meta = {}
    r = parser(url)
    meta['title'] = r.find(id='thread_subject').text
    meta['author'] = r.find(class_='authi').find('a', class_='xw1').text
    meta['original'] = url
    return meta

def get_date(url):
    return parser(url).find_all(class_='authi')[1].find('em').text[4:13]

def s1_spider(id):
    url = f'https://bbs.saraba1st.com/2b/thread-{id}-1-1.html'
    lz_url = lz_only(url)
    generator('Stage1', get_meta(lz_url), get_posts(lz_url), get_date(lz_url))

if __name__ == '__main__':
    s1_spider(sys.argv[1])
