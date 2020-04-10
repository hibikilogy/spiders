#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' 上传图片、解析器等 '

import requests
from io import BytesIO
from bs4 import BeautifulSoup
from html2text import html2text
import re


def parser(url, headers=None):
    content = requests.get(url, headers=headers, timeout=10).content
    return BeautifulSoup(content, 'html.parser')


def upload_img(url):
    print('正在使用 sm.ms 上传图片……')
    try:  # sm.ms API v2
        img = BytesIO(requests.get(url).content)
        body = {'smfile': img}
        r = requests.post('https://sm.ms/api/v2/upload', data=None, files=body, timeout=10)
        try:
            with open('img.txt', 'a') as f:
                f.write(f'{r.json()["data"]["url"]}（{r.json()["data"]["delete"]}）\n')
            print('上传成功，地址和删除链接已写入 img.txt。')
            return r.json()['data']['url']
        except KeyError:
            print('上传成功。')
            return r.json()['images']
    except Exception as e:
        try:
            print(f'使用 sm.ms 上传失败（{e}），使用 GitHub 作为图床……')
            filename = url.split('/')[-1]
            with open(f'../hibikilogy.github.io/images/{filename}', 'wb') as f:
                f.write(requests.get(url).content)
            print('上传成功，需提交 hibikilogy.github.io 中的改动方可使用。')
            return f'https://cdn.jsdelivr.net/gh/hibikilogy/hibikilogy.github.io/images/{filename}'
        except FileNotFoundError:
            print(f'上传失败，已使用原链接。请检查是否在上级目录内存在 hibikilogy.github.io 的本地仓库。')
            return url
        except Exception as e:
            print(f'上传失败（{e}），已使用原链接。')
            return url


def html2markdown(text):
    pattern = re.compile(r'<span.*?>.*?</span>')
    spans = pattern.findall(text)
    for index, span in enumerate(spans):
        text = text.replace(span, f'span{index}')
    text = html2text(text)
    for index, span in enumerate(spans):
        text = text.replace(f'span{index}', span)
    return text


def generator(tag, meta, posts, date):
    print('生成文件中……')
    with open(f'{date}-{meta["title"]}.md', 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write('layout: post\n')
        for key in meta:
            f.write(f'{key}: {meta[key]}\n')
        img = re.compile(r'!\[.*\]\((.*)\)')
        try:  # 头图
            header = img.findall(posts)[0]
            f.write(f'header-img: {header}\n')
        except IndexError:
            pass
        f.write('catalog: true\n')
        f.write('tags:\n')
        f.write(f'    - {tag}\n')
        f.write('---\n')
        f.write(posts)
    print(f'{date}={meta["title"]}.md已生成。')
