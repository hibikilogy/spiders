#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from selenium import webdriver
# import random
import html2text
from time import sleep
from bs4 import BeautifulSoup
# from utils import upload_img
from utils import html2markdown
from utils import generator
import sys
import re


""" 使用 selenium 无需用 headers
def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
        'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
        'Opera/9.52 (Windows NT 5.0; U; en)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
        'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00'
        ]
    user_agent = random.choice(user_agents)
    headers = {
        'host': "bbs.nga.cn",
        'connection': "keep-alive",
        'cache-control': "no-cache",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'referer': "http://bbs.ngacn.cc/misc/adpage_insert_2.html?http://bbs.ngacn.cc/read.php?tid=13427591&page=2",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.9",
        'cookie': 'UM_distinctid=165d243d684e9-0111554226bb1c-3c604504-13edd4-165d243d68516f; taihe=aebe409faefff51e20f2dde377f1cea6; ngacn0comUserInfo=%25B0%25EB%25CF%25C4%25A8q%25A5%25A1%258EU%259B%25F6%09%25E5%258D%258A%25E5%25A4%258F%25E2%2595%25AD%25E3%2582%25A1%25E5%25B6%25B6%25E6%25B6%25BC%0939%0939%09%0910%090%090%090%090%09; ngaPassportUid=43320220; ngaPassportUrlencodedUname=%25B0%25EB%25CF%25C4%25A8q%25A5%25A1%258EU%259B%25F6; ngaPassportCid=Z8ltrcjgo616kor6sbbpgr0thdnbrsr96ge8kte5; ngacn0comUserInfoCheck=10d5d900ae3f241cd4bc9d2e144794f3; ngacn0comInfoCheckTime=1537976770; taihe_session=6444150154287a3254e70831f46a8868; CNZZDATA30043604=cnzz_eid%3D364786080-1536830942-%26ntime%3D1537976642; CNZZDATA30039253=cnzz_eid%3D943882560-1536826159-%26ntime%3D1537971608; Hm_lvt_5adc78329e14807f050ce131992ae69b=1536830988,1536839697,1537976774; lastvisit=1537976828; lastpath=/read.php?tid=12689996&page=2; bbsmisccookies=%7B%22insad_refreshid%22%3A%7B0%3A%22/153794231025962%22%2C1%3A1538581572%7D%2C%22pv_count_for_insad%22%3A%7B0%3A-46%2C1%3A1537981224%7D%2C%22insad_views%22%3A%7B0%3A1%2C1%3A1537981224%7D%7D; Hm_lpvt_5adc78329e14807f050ce131992ae69b=1537976834'
        }
    return headers
"""

def get_meta(html, url):
    r = BeautifulSoup(html, 'html.parser')
    meta = {}
    meta['title'] = r.find(id='postsubject0').text
    tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
    meta['title'] = re.sub(tag, '', meta['title'])
    meta['author'] = r.find(id='postauthor0').text  # FIXME 似乎会变为 UID
    meta['original'] = url
    return meta

def get_date(html):
    r = BeautifulSoup(html, 'html.parser')
    date = r.find(id='postdate0').text[:10]
    return date

def get_posts(html):
    r = BeautifulSoup(html, 'html.parser')
    post = str(r.find(id='postcontent0'))
    colors = ('skyblue', 'royalblue', 'blue', 'darkblue',
            'orange', 'orangered', 'crimson', 'red', 'firebrick', 'darkred',
            'green', 'limegreen', 'seagreen', 'teal',
            'deeppink', 'tomato', 'coral', 'purple', 'coral')
    for color in colors:  # NGA 使用 class 渲染颜色
        post = post.replace(f'class="{color}"', f'style="color: {color};"')
    post = post.replace('src', 'fake')
    post = post.replace('data-fakelazy', 'src')
    # NGA 图床可以外部引用，无需图床
    # img_src = r"""\bsrc\b\s*=\s*[\'\"]?([^\'\"]*)[\'\"]?"""
    # for img in re.findall(img_src, post):
    #     new_img = upload_img(img)
    #     post = post.replace(img, new_img)
    post = html2markdown(post)
    return post

def nga_spider(id):
    url = f'https://bbs.nga.cn/read.php?tid={id}'
    try:
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        browser = webdriver.Firefox(options=options)
    except WebDriverException:
        options = webdriver.chrome.options()
        options.add_argument('-headless')
        browser = webdriver.Chrome(options=options)
    # 打开隐藏部分
    click_button = """
    document.querySelectorAll(".collapse_btn button").forEach(function(each){each.click()})
    """
    browser.get(url)
    sleep(15)  # 让 NGA 自己渲染 bbcode
    browser.execute_script(click_button)
    content = browser.execute_script('return document.querySelector("html").innerHTML;')
    browser.close()
    generator('NGA', get_meta(content, url), get_posts(content), get_date(content))

if __name__ == '__main__':
    nga_spider(str(sys.argv[1]))
