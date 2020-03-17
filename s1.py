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

def lz_only(url):
    suffix = parser(url).find_all(class_='authi')[1].find('a')['href']
    return f'https://bbs.saraba1st.com/2b/{suffix}'

def get_posts(url):
    def get_post(page_url):
        return parser(page_url).find_all(class_='t_fsz')
    # page = parser(url).find(id='fj').find('input')['size']
    posts = []
    # for i in range(1, int(page) + 1):
    #    posts += [x for x in get_post(url[:-8] + str(i) + '-1.html')]
    content = ''
    posts = get_post(url)
    # FIXME
    pstatus = r'<i class="pstatus">.+?<\/i>'
    img_src = r"""\bsrc\b\s*=\s*[\'\"]?([^\'\"]*)[\'\"]?""" 
    for post in posts:
        post = str(post)
        post = re.sub('<div[^>]*>', '<p>', post)
        post = re.sub('<\/div[^>]*>', '</p>', post)
        re.sub(pstatus, '', post)
        for img in re.findall(img_src, post):
            new_img = upload_img(img)
            post = post.replace(img, new_img)
        content += html2text.html2text(post)
    return content

def get_meta(url):
    meta = {}
    r = parser(url)
    meta['title'] = r.find(id='thread_subject').text
    meta['author'] = r.find(class_='authi').find('a', class_='xw1').text
    meta['original'] = url
    return meta

def get_date(url):
    return parser(url).find_all(class_='authi')[1].find('em').text[4:13]

def generator(meta, posts, date):
    print('生成文件中……')
    with open(f'{date}-{meta["title"]}.md', 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write('layout: post\n')
        for key in meta:
            f.write(f'{key}: {meta[key]}\n')
        f.write(f'catalog: true\n')
        f.write(f'tags:\n')
        f.write(f'    - Stage1\n')
        f.write('---\n')
        f.write(posts)
    print(f'{date}={meta["title"]}.md已生成。')

if __name__ == '__main__':
    url = 'https://bbs.saraba1st.com/2b/thread-' + input('请输入帖子 ID：') +'-1-1.html'
    lz_url = lz_only(url)
    generator(get_meta(lz_url), get_posts(lz_url), get_date(lz_url))
