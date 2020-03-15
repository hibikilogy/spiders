# -*- coding: utf-8 -*-
import requests
import re
import html2text
from bs4 import BeautifulSoup
from io import BytesIO

def parser(url):
    return BeautifulSoup(requests.get(url).content, 'html.parser')

def get_posts(url):
    def get_post(page_url):
        return parser(page_url).find_all(class_='d_post_content')
    page = parser(url).find_all('li', class_='l_reply_num')[0].find_all('span')[1].text
    posts = []
    for i in range(1, int(page) + 1):
        posts += [x for x in get_post(url + '&pn=' + str(i))]
    content = ''
    for post in posts:
        post = str(post)
        post = re.sub('<div[^>]*>', '<p>', post)
        post = re.sub('<\/div[^>]*>', '</p>', post) 
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

def generator(meta, posts, date):
    with open(f'{date}-{meta["title"]}.md', 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write('layout: post\n')
        for key in meta:
            f.write(f'{key}: {meta[key]}\n')
        f.write(f'catalog: true\n')
        f.write('---\n')
        f.write(posts)
    return meta

# FIXME
def upload_img(posts):
    type = requests.get(url).headers['Content-Type']
    img = BytesIO(requests.get(url).content)
    headers = {'Content-Type': type}
    body = {'smfile': img}
    r = requests.post('https://sm.ms/api/v2/upload', headers=headers, files=body)
    return r.data.url

if __name__ == '__main__':
    url = 'https://tieba.baidu.com/p/6476296121?see_lz=1'
    generator(get_meta(url), get_posts(url), get_date(url))
