# 爬虫参数&配置文件
import argparse, os

class CrawlerConfig():
    # 参数查找顺序：命令行参数传入>config值>命令行参数默认值
    def __init__(self):
        # config
        self.ids = [4856222]
        self.driver_path = r'E:\software\common\webBrowser\chrome\chromedriver.exe'
        self.upload_url = 'https://sm.ms/api/v2/upload' #第三方图床
        self.project_path = '../hibikilogy.github.io'   #本地仓库根路径
        self.max_retry = 3
        self.max_timeout = 10
        
        self.upload_img = False
        self.origin_img = False
        self.origin_quality = False
        self.static = False
        
        # self.project_path = os.path.abspath(self.project_path)
            
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--static","-s", action="store_true", default=False, help="Whether to use static mode(simpler & faster but easy to be banned), default False")
        parser.add_argument("--upload_img","-u", action="store_true", default=False, help="Whether to upload imgs via third-party img hosting service, please change your upload_url in config, default False")
        parser.add_argument("--origin_img","-o", action="store_true", default=False, help="Whether to use original img url directly, default False")
        parser.add_argument("--origin_quality","-q", action="store_true", default=False, help="Whether to use/download img of original quality without compression, default False")
        parser.add_argument("--driver_path", type=str, default="chromedriver.exe", help="Path to chrome driver")
        parser.add_argument("--id","-id", nargs='+', type=str, default=[], help="List of post ids")
        
        args = parser.parse_args()
        if args.upload_img != parser.get_default('upload_img'):
            self.upload_img = args.upload_img
        if args.origin_img != parser.get_default('origin_img'):
            self.origin_img = args.origin_img
        if args.origin_quality != parser.get_default('origin_quality'):
            self.origin_quality = args.origin_quality
        if args.static != parser.get_default('static'):
            self.static = args.static
        if os.path.exists(args.driver_path):
            self.driver_path = args.driver_path
        if args.id:
            self.ids = args.id
        return args