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

def get_posts(url):
    def get_post(page_url):
        return parser(page_url).find_all(class_='d_post_content')
    page = parser(url).find_all('li', class_='l_reply_num')[0].find_all('span')[1].text
    posts = []
    for i in range(1, int(page) + 1):
        posts += [x for x in get_post(url + '&pn=' + str(i))]
    content = ''
    img_src = r"""\bsrc\b\s*=\s*[\'\"]?([^\'\"]*)[\'\"]?""" 
    for post in posts:
        post = str(post)
        post = re.sub('<div[^>]*>', '<p>', post)
        post = re.sub('<\/div[^>]*>', '</p>', post)
        for img in re.findall(img_src, post):
            new_img = upload_img(img)
            post = post.replace(img, new_img)
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
    print('生成文件中……')
    with open(f'{date}-{meta["title"]}.md', 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write('layout: post\n')
        for key in meta:
            f.write(f'{key}: {meta[key]}\n')
        f.write(f'catalog: true\n')
        f.write(f'tags:\n')
        f.write(f'    - 贴吧\n')
        f.write('---\n')
        f.write(posts)
    print(f'{date}={meta["title"]}.md已生成。')

if __name__ == '__main__':
    url = 'https://tieba.baidu.com/p/' + input('请输入帖子 ID：') + '?see_lz=1'
    generator(get_meta(url), get_posts(url), get_date(url))
