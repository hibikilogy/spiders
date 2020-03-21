#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' 上传图片、解析器等 '

import requests
from io import BytesIO
from bs4 import BeautifulSoup


def parser(url, headers=None):
    return BeautifulSoup(requests.get(url, headers=headers, timeout=10).content, 'html.parser')


# sm.ms API v2
def upload_img(url):
    print('上传图片中……')
    try:
        img = BytesIO(requests.get(url).content)
        body = {'smfile': img}
        r = requests.post('https://sm.ms/api/v2/upload', data=None, files=body, timeout=10)
        try:
            with open('img.txt', 'a') as f:
                f.write(f'{r.json()["data"]["url"]}，删除：{r.json()["data"]["delete"]}\n')
            print('图片上传成功，地址和删除链接已写入 img.txt。')
            return r.json()['data']['url']
        except KeyError:
            print('图片已存在，无法得知删除链接。')
            return r.json()['images']
    except Exception as e:
        print(f'上传失败（{e}），已使用原链接。')
        return url


def generator(tag, meta, posts, date):
    print('生成文件中……')
    with open(f'{date}-{meta["title"]}.md', 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write('layout: post\n')
        for key in meta:
            f.write(f'{key}: {meta[key]}\n')
        f.write('catalog: true\n')
        f.write('tags:\n')
        f.write(f'    - {tag}\n')
        f.write('---\n')
        f.write(posts)
    print(f'{date}={meta["title"]}.md已生成。')

