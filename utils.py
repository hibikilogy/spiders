#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' 上传图片、解析器等 '

import os,random,re
from io import BytesIO
from collections import namedtuple, OrderedDict
from convert import JekyllFront
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from html2text import html2text

import blurhash
from base64 import urlsafe_b64encode

FRONT = namedtuple('front', ['separator', 'definer', 'commenter', 'wrapper'])

SYMBOL = OrderedDict({
    "jekyll": {
        "separator": "---",
        "definer": ":",
        "commenter": "#",
        "wrapper": "",
    },
    "zola": {
        "separator": "+++",
        "definer": "=",
        "commenter": "#",
        "wrapper": "\"",
    }
})

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
    
    special_chars = r'[——、<>:"/\\|?*\x00-\x1F\x7F]'    #替换文件系统的特殊字符
    
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
            os.makedirs(dir,exist_ok=True)
            with open(f'{dir}/{filename}', 'wb') as f:
                f.write(r.content)
            print('本地图像下载成功，需提交 hibikilogy.github.io 中的改动方可使用。')
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
    os.makedirs('temp',exist_ok=True)
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





def extract_wh_from(text, type):
    if type == "style":
        pattern = r'width\s*?:\s*?(\d+)(?:\.\d+)?.*?height\s*?:\s*?(\d+)(?:\.\d+)?|height\s*?:\s*?(\d+)(?:\.\d+)?.*?width\s*?:\s*?(\d+)(?:\.\d+)?'
    elif type == "attr":
        pattern = r'width\s*?=\s*?"(\d+)(?:\.\d+)?".*?height\s*?=\s*?"(\d+)(?:\.\d+)?"|height\s*?=\s*?"(\d+)(?:\.\d+)?".*?width\s*?=\s*?"(\d+)(?:\.\d+)?"'
    elif type == "elem":
        w = text.size.get('width')
        h = text.size.get('height')
        return w,h
    else:
        raise ValueError("Unknown parttern type for width and height")
    match = re.search(pattern, text)

    if match:
        if match.group(1) and match.group(2):
            width = match.group(1)
            height = match.group(2)
        elif match.group(3) and match.group(4):
            width = match.group(4)
            height = match.group(3)
        return width, height
    else:
        return None, None

def extract_wh(text):
    w,h = extract_wh_from(text,'style')
    if w or h:
        return w, h
    w,h = extract_wh_from(text, 'attr')
    return w, h

def get_img_size(img,format):
    buffer = BytesIO()
    img.save(buffer, format=format)
    size_in_kb = buffer.tell()/1024
    buffer.close()
    return size_in_kb
class Crawler():
    def __init__(self, cfg):
        self.headers = {
            'User-Agent':random.choice(USER_AGENT_LIST)
        } 
        self.cfg = cfg
        self.meta = {}
        self.post = None
        self.driver = None
        self.frontter = FRONT(
            separator=SYMBOL[cfg.front]["separator"], 
            definer=SYMBOL[cfg.front]["definer"],
            commenter=SYMBOL[cfg.front]["commenter"],
            wrapper=SYMBOL[cfg.front]["wrapper"],
            )
        # self.isDownload = False
    
    def waiting(self, wait=None, msg=None):
        for i in range(self.cfg.max_retry):
            try:
                WebDriverWait(self.driver, self.cfg.max_timeout).until(wait)
                return True
            except TimeoutException:
                print(f"Attempt {i + 1}/{self.cfg.max_retry} failed: Timeout. {msg}")
        return False
    
    def scoll_bottom(self, operation = None):
        operated = False
        # 获取页面的总高度
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        # 设置每次滑动的距离
        current_position = 0
        while current_position < last_height:
            # 执行 JavaScript 滑动页面
            self.driver.execute_script(f"window.scrollTo(0, {current_position});")
            # 等待页面加载
            time.sleep(self.cfg.scroll_delay)
            if operation != None and not operated:
                operated = operation()
            # 更新当前位置
            current_position += self.cfg.scroll_increment
        # 确保滑动到页面的最底部
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def static_parser(self, url, headers=None):
        content = requests.get(
            url, headers=self.headers if headers==None else headers, timeout=self.cfg.max_timeout
            ).content
        return BeautifulSoup(content, 'html.parser')
    
    def dynamic_parser(self, url):
        #NOTE: 需要chromedriver路径,下载：https://googlechromelabs.github.io/chrome-for-testing/#stable
        self.driver = webdriver.Chrome(service=Service(self.cfg.driver_path))  
        self.driver.get(url)
        return BeautifulSoup(self.driver.page_source, 'html.parser')
        
    def parser(self,url):
        if self.cfg.static:
            return self.static_parser(url)
        else:
            return self.dynamic_parser(url)
        
    def download_img(self, url, w, h):
        try:
            ext = 'gif' if 'gif' in url else self.cfg.format
            r = requests.get(url,headers=self.headers)
            r.raise_for_status()
            image = Image.open(BytesIO(r.content))
            if self.cfg.size_thr<=0:
                ...
            elif get_img_size(image,ext) > self.cfg.size_thr:
                w,h = map(min,zip([w*2,h*2],(image.size[0]//2, image.size[1]//2)))
                image = image.resize((w, h),Image.LANCZOS)
            w,h = image.size
            hash = blurhash.encode(image.copy(), x_components=3, y_components=2)
            hash64 = urlsafe_b64encode(hash.encode('ascii')).decode('ascii')
            filename = f"{hash64}{f'.w{w}' if w else ''}{f'.h{h}' if h else ''}.{ext}"
            dir = f"{self.cfg.project_path}/images/{self.meta['date']}"
            os.makedirs(dir,exist_ok=True)
            image.save(f'{dir}/{filename}', format=ext)
            # with open(f'{dir}/{filename}', 'wb') as f: 
            #     f.write(r.content)
            print(f'本地图像下载成功({w}_{h}_{get_img_size(image,ext):.2f}KB),需提交hibikilogy.github.io中的改动上传。')
            # self.isDownload = True
            image.close()
            return f"../images/{self.meta['date']}/{filename}"
        except requests.exceptions.RequestException as e:
            print("网络错误，无法下载图像:", e)
        except FileNotFoundError:
            print(f'创建文件失败，使用原链接。请检查是否在上级目录内存在 hibikilogy.github.io 的本地仓库。')
        except Exception as e:
            print(f'下载失败（{e}），使用原链接。')
        image.close()
        return url
    
    def handle_img(self, url, w, h):
        '''可配置使用原链接,上传三方图床,默认下载到本地'''
        if self.cfg.origin_img:     # 使用原图床
            return url
        if self.cfg.upload_img:     # 尝试上传
            print(f'正在使用{self.cfg.upload_url}上传图片……')
            try:  # TODO: 弃用
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
                print(f'上传失败（{e}），使用 GitHub 作为图床……')
        return self.download_img(url, w, h)
    
    def html2markdown(self):
        pattern = re.compile(r'<span.*?>.*?</span>')
        spans = pattern.findall(self.post)
        for index, span in enumerate(spans):
            self.post = self.post.replace(span, f'span{index}')
        self.post = html2text(self.post)
        for index, span in enumerate(spans[::-1], start=1):
            self.post = self.post.replace(f'span{len(spans) - index}', span)
        return self.post            

    def gen_title(self):
        
        if 'title' in self.meta:
            title = clean_chars(self.meta['title'])
        else:
            title = self.meta['original'].split('/')[-1]
        return title
    
    def jekyll_front(self, tag):
        sep = self.frontter.separator
        defi = self.frontter.definer
        wrap = self.frontter.wrapper
        res = f'{sep}\n'
        res += f'layout{defi}post\n'
        for key in self.meta:
            res +=f'{key}{defi}{wrap}{self.meta[key]}{wrap}\n'
        res += f'catalog{defi}{wrap}true{wrap}\n'
        res += f'tags{defi}\n'
        res += f'    - {tag}\n'
        res +=f'{sep}\n'
        return res

    def zola_front(self, tag):
        sep = self.frontter.separator
        res = f'{sep}\n'
        res += JekyllFront(**self.meta).to_zola_front().to_toml()
        res += f'{sep}\n'
        return res
    
    def generator(self, tag, custom_fname=''):
        print('生成文件中……')
        dir = f"{self.cfg.project_path}/temp"
        os.makedirs(dir,exist_ok=True)
        if custom_fname == '':  
            cleaned_fname = self.gen_title()
        else:
            cleaned_fname = custom_fname
        with open(f"{dir}/{self.meta['date']}-{cleaned_fname}.md", 'w', encoding='utf-8') as f:
            if self.cfg.front == 'jekyll':
                f.write(self.jekyll_front(tag))
            elif self.cfg.front == 'zola':
                f.write(self.zola_front(tag))
            f.write(self.post)
        print(
            f"{dir}/{self.meta['date']}-{cleaned_fname}.md 已生成,\n\t需将文件移至_post提交"
            # +f'{", 提交时message需添加 _path2url 关键字" if self.isDownload else ""}'
            )
    
if __name__ == '__main__':
    ...