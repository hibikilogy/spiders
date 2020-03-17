# -*- coding: utf-8 -*-
import requests
import re
import html2text
from bs4 import BeautifulSoup
from io import BytesIO

def parser(url):
    return BeautifulSoup(requests.get(url).content, 'html.parser')

# sm.ms API v2
def upload_img(url):
    print('上传图片中……')
    try:
        requests.get('https://sm.ms')
        img = BytesIO(requests.get(url).content)
        body = {'smfile': img}
        r = requests.post('https://sm.ms/api/v2/upload', data=None, files=body)
        try:
            print(f'图片上传成功，删除链接：{r.json()["data"]["delete"]}')
            return r.json()['data']['url']
        except KeyError:
            print('图片已存在，无法得知删除链接。')
            return r.json()['images']
    except requests.exceptions.ConnectionError:
        print('图床连接失败，已使用原链接。')
        return url

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
