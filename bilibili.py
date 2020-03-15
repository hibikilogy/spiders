# -*- coding: utf-8 -*-
import requests
import html2text
from bs4 import BeautifulSoup
import time

def parser(url):
    return BeautifulSoup(requests.get(url).content, 'html.parser')

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
    """ post = re.sub('<p[^>]*>', '', post)
    post = re.sub('<\/p[^>]*>', '<br>', post) """
    post = html2text.html2text(post)
    return post

def generator(meta, posts, date):
    print('正在爬取……')
    with open(f'{date}-{meta["title"]}.md', 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write('layout: post\n')
        for key in meta:
            f.write(f'{key}: {meta[key]}\n')
        f.write(f'catalog: true\n')
        f.write('---\n')
        f.write(posts)
    print(f'{date}-{meta["title"]}.md已生成。')

if __name__ == '__main__':
    url = 'https://www.bilibili.com/read/cv' + input('请输入文章 cv 号：')
    generator(get_meta(url), get_posts(url), get_date(url))
