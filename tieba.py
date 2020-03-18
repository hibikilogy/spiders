#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import html2text
from utils import parser
from utils import upload_img
from utils import generator


def get_posts(url):
    def get_post(page_url):
        return parser(page_url).find_all(class_='d_post_content')
    page = parser(url).find_all('li', class_='l_reply_num')[0].find_all('span')[1].text
    posts = []
    for i in range(1, int(page) + 1):
        posts += [x for x in get_post(url + '&pn=' + str(i))]
    content = ''
    img_src = r"""\bsrc\b\s*=\s*[\'\"]?([^\'\"]*)[\'\"]?""" 
    for post in posts:
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
    meta['title'] = r.find(class_='core_title_txt').text
    meta['author'] = r.find('a', class_='p_author_name').text
    meta['original'] = url
    return meta

def get_date(url):
    return parser(url).find_all(class_='tail-info')[2].text[:10]

if __name__ == '__main__':
    url = 'https://tieba.baidu.com/p/' + input('请输入帖子 ID：') + '?see_lz=1'
    generator('贴吧', get_meta(url), get_posts(url), get_date(url))
