
# -*- coding: utf-8 -*-
import re
from utils import extract_wh_from
from config import CrawlerConfig
from utils import Crawler
import selenium.webdriver.support.expected_conditions as EC


DOM_DB={
    "url": "https://douban.com/review/",
    # "waiter": ('xpath', "//div[contains(@class, 'signQr-container')]"),
    # "clicker": ('xpath', "//button[contains(text(), '取消')]"),
    "date": ('xpath', "//div[contains(@class, 'main-meta')]/span[1]"),
    "content": ('xpath', "//div[contains(@class, 'review-content')]"),
    "title": ('xpath', "//div/h1/span"),
    "author": ('xpath', "//header/a/span"),
    "img": ("xpath", "//div[contains(@class, 'image-wrapper')]/img"),
    # "cover": ("xpath", "//div/div/img")
    }

def id_check(id):
    return id != "" and (isinstance(id, int) or id.isdigit())


def get_meta(spider,id,cDOM):
    url = f'{cDOM["url"]}{id}'
    spider.parser(url, wait = EC.visibility_of_element_located(cDOM['date']), msg = "等待页面加载...") 
    if "waiter" in cDOM:
        spider.waiting(EC.invisibility_of_element_located(cDOM['waiter']), msg = "请在浏览器界面登录...") 
    
    def trans_img_url(elem,url):
        w,h = extract_wh_from(elem,'elem')
        return spider.download_img(url, w,h)
    
    spider.scoll_bottom()
    
    # meta
    date_elem = spider.driver.find_element(*cDOM["date"])
    spider.meta['date'] = date_elem.text.split()[0]
    
    title_elem = spider.driver.find_element(*cDOM["title"])
    if title_elem:
        spider.meta['title'] = title_elem.text.strip()
        tag = r'\[.*?\]|【.*?】'  # 去除【】[] 包裹的内容
        spider.meta['title'] = re.sub(tag, '', spider.meta['title'])
    spider.meta['author'] = spider.driver.find_element(*cDOM["author"]).text.strip()
    spider.meta['original'] = url
    
    # post
    post_content = spider.driver.find_element(*cDOM["content"])
    spider.post = post_content.get_attribute("outerHTML")
    
    # img
    imgs = spider.driver.find_elements(*cDOM["img"])
    for idx,img in enumerate(imgs):
        origin_img = img.get_attribute("src")
        if origin_img:
            new_img = trans_img_url(img, origin_img)
            spider.post = spider.post.replace(origin_img, new_img)
            if idx == 0:
                spider.meta['header-img'] = new_img
    if "cover" in cDOM:
        try:
            img = spider.driver.find_element(*cDOM["cover"])
            origin_img = img.get_attribute("src")
            spider.meta['header-img'] = trans_img_url(img, origin_img)
            spider.post = spider.post.replace(origin_img, new_img)
        except Exception as e:
            ...
    spider.driver.quit()
    spider.html2markdown()
    


def bgm_spider(cfg):
    for idx, id in enumerate(cfg.ids):   
        if not id_check(id):
            continue
        cDOM = DOM_DB
            
        spider = Crawler(cfg)
        get_meta(spider,id,cDOM)
        custom_fname = cfg.fname[idx] if idx < len(cfg.fname) else ''
        spider.generator('douban', custom_fname)

if __name__ == '__main__':
    cfg = CrawlerConfig('config.json','douban')
    bgm_spider(cfg)
