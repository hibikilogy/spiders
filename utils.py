#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' 上传图片、解析器等 '

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os,random
from io import BytesIO
from bs4 import BeautifulSoup
from html2text import html2text
import re

USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
]

default_headers = {
            'User-Agent':random.choice(USER_AGENT_LIST)
        }

def clean_chars(text):
    # 定义全角标点与对应的半角标点的映射关系
    punctuation_mapping = {
        '，': ',',
        '。': '.',
        '！': '!',
        '？': '?',
        '‘': '\'',
        '’': '\'',
        '（': '(',
        '）': ')',
        '：': ':',
    }
    
    special_chars = r'[<>:"/\\|?*\x00-\x1F\x7F]'    #替换文件系统的特殊字符
    
    pattern = '|'.join(re.escape(p) for p in punctuation_mapping.keys())
    result = re.sub(pattern, lambda m: punctuation_mapping[m.group()], text)
    result = re.sub(special_chars, '_', result)
    return result


def html2markdown(text):
    pattern = re.compile(r'<span.*?>.*?</span>')
    spans = pattern.findall(text)
    for index, span in enumerate(spans):
        text = text.replace(span, f'span{index}')
    text = html2text(text)
    for index, span in enumerate(spans[::-1], start=1):
        text = text.replace(f'span{len(spans) - index}', span)
    return text

def parser(url,headers=None):
    content = requests.get(url, headers=headers if headers else default_headers, timeout=10).content
    return BeautifulSoup(content, 'html.parser')

def upload_img(url,date = None):
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
            r = requests.get(url,headers=default_headers)
            r.raise_for_status()
            filename = url.split('/')[-1]
            dir = f"../hibikilogy.github.io/images/{date}"
            if not os.path.exists(dir):
                os.makedirs(dir)
            with open(f'{dir}/{filename}', 'wb') as f:
                f.write(r.content)
            print('本地写入成功，需提交 hibikilogy.github.io 中的改动方可使用。')
            return f'https://cdn.jsdelivr.net/gh/hibikilogy/hibikilogy.github.io/images/{filename}'
        except requests.exceptions.RequestException as e:
            print("无法下载图像:", e)
        except FileNotFoundError:
            print(f'上传失败，已使用原链接。请检查是否在上级目录内存在 hibikilogy.github.io 的本地仓库。')
            return url
        except Exception as e:
            print(f'上传失败（{e}），已使用原链接。')
            return url

def generator(tag, meta, date, posts):
    print('生成文件中……')
    if not os.path.exists('temp'):
        os.makedirs('temp')
    cleaned_title = clean_chars(meta['title'])
    with open(f'temp/{date}-{cleaned_title}.md', 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write('layout: post\n')
        for key in meta:
            f.write(f'{key}: {meta[key]}\n')
        f.write('catalog: true\n')
        f.write('tags:\n')
        f.write(f'    - {tag}\n')
        f.write('---\n')
        f.write(posts)
    print(f'temp/{date}-{cleaned_title}.md已生成。')

class Crawler():
    def __init__(self, cfg):
        # self.url = url
        self.headers = {
            'User-Agent':random.choice(USER_AGENT_LIST)
        } 
        self.cfg = cfg
        
    def static_parser(self, url, headers=None):
        content = requests.get(
            url, headers=self.headers if headers==None else headers, timeout=self.cfg.max_timeout
            ).content
        return BeautifulSoup(content, 'html.parser')
    
    def dynamic_parser(self, url):
        #NOTE: 需要chromedriver路径,下载：https://googlechromelabs.github.io/chrome-for-testing/#stable
        service = Service(self.cfg.driver_path)
        driver = webdriver.Chrome(service=service)  
        driver.get(url)
        return BeautifulSoup(driver.page_source, 'html.parser')

    def upload_img(self, url,date = None):
        if not self.cfg.args.upload_img:
            return url
        print('正在使用 sm.ms 上传图片……')
        try:  # sm.ms API v2
            img = BytesIO(requests.get(url).content)
            body = {'smfile': img}
            r = requests.post(self.cfg.upload_url, data=None, files=body, timeout=10)
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
                r = requests.get(url,headers=self.headers)
                r.raise_for_status()
                filename = url.split('/')[-1]
                dir = f"{self.cfg.img_save_path}/{date}"
                if not os.path.exists(dir):
                    os.makedirs(dir)
                with open(f'{dir}/{filename}', 'wb') as f:
                    f.write(r.content)
                print('本地写入成功，需提交 hibikilogy.github.io 中的改动方可使用。')
                return f'{self.cfg.img_root_url}/{date}/{filename}'
            except requests.exceptions.RequestException as e:
                print("无法下载图像:", e)
            except FileNotFoundError:
                print(f'上传失败，已使用原链接。请检查是否在上级目录内存在 hibikilogy.github.io 的本地仓库。')
                return url
            except Exception as e:
                print(f'上传失败（{e}），已使用原链接。')
                return url
    
    def generator(self, tag, meta, date, posts):
        print('生成文件中……')
        if not os.path.exists(self.cfg.post_save_path):
            os.makedirs(self.cfg.post_save_path)
        cleaned_title = clean_chars(meta['title'])
        with open(f'{self.cfg.post_save_path}/{date}-{cleaned_title}.md', 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write('layout: post\n')
            for key in meta:
                f.write(f'{key}: {meta[key]}\n')
            f.write('catalog: true\n')
            f.write('tags:\n')
            f.write(f'    - {tag}\n')
            f.write('---\n')
            f.write(posts)
        print(f'{self.cfg.post_save_path}/{date}-{cleaned_title}.md已生成。')
    
