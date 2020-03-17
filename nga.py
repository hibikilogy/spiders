# -*- coding: utf-8 -*-
import requests
import re
import random
import html2text
import bbcode
from bs4 import BeautifulSoup
from io import BytesIO

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

def parser(url):
    return BeautifulSoup(requests.get(url, headers=get_headers()).content, 'html.parser')

# FIXME
def bb2md(str):
    bbcode.Parser().add_simple_formatter('img', '<img src="%(value)s" />')
    return html2text.html2text(bbcode.Parser().format(str))

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
    meta['title'] = r.find(id='postsubject0').text
    meta['author'] = r.find(id='postauthor0').text
    meta['original'] = url
    return meta

def get_date(url):
    date = parser(url).find(id='postdate0').text[:10]
    return date

def get_posts(url):
    r = parser(url)
    post = str(r.find(id='postcontent0'))
    post = post.replace('data-src', 'src')
    # img_src = r"""\bsrc\b\s*=\s*[\'\"]?([^\'\"]*)[\'\"]?"""
    # for img in re.findall(img_src, post):
    #     new_img = upload_img(img)
    #     post = post.replace(img, new_img)
    post = bb2md(post)
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
        f.write(f'    - NGA\n')
        f.write('---\n')
        f.write(posts)
    print(f'{date}-{meta["title"]}.md已生成。')

if __name__ == '__main__':
    url = 'https://bbs.nga.cn/read.php?tid=' + input('请输入帖子 ID：')
    generator(get_meta(url), get_posts(url), get_date(url))
