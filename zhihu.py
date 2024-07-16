
# -*- coding: utf-8 -*-
import re, time
from utils import extract_wh_from
from config import CrawlerConfig
from utils import Crawler
import selenium.webdriver.support.expected_conditions as EC

DOM_QA={
    "waiter": ('xpath', "//div[contains(@class, 'signQr-container')]"),
    "clicker": ('xpath', "//button[contains(text(), '取消')]"),
    "date": ('xpath', "//div[contains(@class, 'ContentItem-time')]/a/span"),
    "content": ('xpath', "//span[contains(@class, 'RichText')]"),
    "title": ('xpath', "//div[contains(@class, 'QuestionHeader-title')]"),
    "author": ('xpath', "//div[contains(@class, 'AuthorInfo-head')]"),
    "img": ("xpath", "//img[contains(@class, 'origin_image')]")
    }

def id_check(id):
    return id != "" and (isinstance(id, int) or id.isdigit())


def get_meta(spider,url):
    cDOM = DOM_QA 
    spider.parser(url, wait = EC.visibility_of_element_located(cDOM['date']), msg = "等待页面加载...") 
    spider.waiting(EC.invisibility_of_element_located(cDOM['waiter']), msg = "请在浏览器界面登录...") 
    
    def trans_img_url(elem,url):
        w,h = extract_wh_from(elem,'elem')
        return spider.download_img(url, w,h)
    
    clicked = False
    def click_elem():
        try:
            spider.driver.find_element(*cDOM["clicker"]).click() # 单击元素
            return True
        except:
            return False
    
    # 获取页面的总高度
    last_height = spider.driver.execute_script("return document.body.scrollHeight")
    # 设置每次滑动的距离
    scroll_increment = 300  # 每次滑动的距离，可以根据需要调整
    delay = 0.1  # 每次滑动后的延迟时间（秒），可以根据需要调整

    current_position = 0
    while current_position < last_height:
        # 执行 JavaScript 滑动页面
        spider.driver.execute_script(f"window.scrollTo(0, {current_position});")
        # 等待页面加载
        time.sleep(delay)
        if not clicked:
            clicked = click_elem()
        # 更新当前位置
        current_position += scroll_increment
    # 确保滑动到页面的最底部
    spider.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # meta
    date_elem = spider.driver.find_element(*cDOM["date"])
    spider.meta['date'] = date_elem.get_attribute("data-tooltip").split()[1]
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
    spider.post = re.sub(r'<noscript.*?noscript>', '', spider.post)
    spider.post = re.sub(r'<path.*?path>', '', spider.post)
    
    # img
    # spider.driver.fullscreen_window()
    imgs = spider.driver.find_elements(*cDOM["img"])
    for idx,img in enumerate(imgs):
        origin_img = img.get_attribute("src")
        if origin_img:
            new_img = trans_img_url(img, origin_img)
            spider.post = spider.post.replace(origin_img, new_img)
            if idx == 0:
                spider.meta['header-img'] = new_img
    spider.driver.quit()
    spider.html2markdown()
    


def bgm_spider(cfg):
    for idx, id in enumerate(cfg.ids):   
        if not id_check(id):
            continue
        url = f'https://www.zhihu.com/answer/{id}'

        spider = Crawler(cfg)
        get_meta(spider,url)
        custom_fname = cfg.fname[idx] if idx < len(cfg.fname) else ''
        spider.generator('zhihu', custom_fname)

if __name__ == '__main__':
    cfg = CrawlerConfig('config.json','zhihu')
    bgm_spider(cfg)
