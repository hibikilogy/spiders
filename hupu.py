# -*- coding: utf-8 -*-
import requests
import html2text
from bs4 import BeautifulSoup

def parser(url):
    return BeautifulSoup(requests.get(url).content, 'html.parser')

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
    post = html2text.html2text(post)
    return post

def generator(meta, posts, date):
    print('生成文件中……')
    with open(f'{date}-{meta["title"]}.md', 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write('layout: post\n')
        for key in meta:
            f.write(f'{key}: {meta[key]}\n')
        f.write(f'catalog: true\n')
        f.write(f'tags:\n')
        f.write(f'    - 虎扑\n')
        f.write('---\n')
        f.write(posts)
    print(f'{date}-{meta["title"]}.md已生成。')

if __name__ == '__main__':
    url = 'https://bbs.hupu.com/' + input('请输入帖子 ID：') + '.html'
    generator(get_meta(url), get_posts(url), get_date(url))
