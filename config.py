# 爬虫参数&配置文件
import argparse, os

class CrawlerConfig():
    def __init__(self):
        self.ids = [4856222]
        self.driver_path = r'E:\software\common\webBrowser\chrome\chromedriver.exe'
        self.upload_url = 'https://sm.ms/api/v2/upload' #第三方图床
        self.img_root_url = 'https://cdn.jsdelivr.net/gh/hibikilogy/hibikilogy.github.io/images'    #github图像路径
        self.img_save_path = '../hibikilogy.github.io/images'   #本地图像保存路径
        self.post_save_path = './temp'  #本地post保存路径
        self.max_retry = 3
        self.max_timeout = 10
        # self.parse_args()
            
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--static","-s", action="store_true", default=False, help="Whether to use static mode, default False")
        parser.add_argument("--upload_img","-u", action="store_true", default=False, help="Whether to upload imgs, default False")
        parser.add_argument("--driver_path", type=str, default="chromedriver.exe", help="Path to chrome driver")
        parser.add_argument("--id", nargs='+', type=str, default=[], help="List of post ids")
        
        self.args = parser.parse_args()
        
        # if self.args['driver_path'] != parser.get_default('driver_path'):
        if os.path.exists(self.args.driver_path):
            self.driver_path = self.args.driver_path
        if self.args.id:
            self.ids = self.args.id
        return self.args