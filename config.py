# 爬虫参数&配置文件
import argparse, os, json

class CrawlerConfig():
    # 参数查找顺序：命令行参数传入>config值>命令行参数默认值
    def __init__(self, config_file, site):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        parser = argparse.ArgumentParser()
        parser.add_argument("--static","-s", action="store_true", default=False, help="Whether to use static mode(simpler & faster but easy to be banned), default False")
        parser.add_argument("--upload_img","-u", action="store_true", default=False, help="Whether to upload imgs via third-party img hosting service, please change your upload_url in config, default False")
        parser.add_argument("--origin_img","-o", action="store_true", default=False, help="Whether to use original img url directly, default False")
        parser.add_argument("--origin_quality","-q", action="store_true", default=False, help="Whether to use/download img of original quality without compression, default False")
        parser.add_argument("--driver_path", type=str, default="chromedriver.exe", help="Path to chrome driver")
        parser.add_argument("--id","-id", nargs='+', type=str, default=[], help="List of post ids")
        parser.add_argument("--fname","-n", nargs='+', type=str, default=[], help="List of post custom file names")
        #bili
        parser.add_argument("--bili.is_dyn","-b.t", action="store_true", default=False, help="Take ids as bilibili dynamic post")
        
        args = parser.parse_args()
        def get_arg(key,default = None):
            key_parts = key.split('.')
            if hasattr(args, key_parts[-1]) and getattr(args, key_parts[-1]) != parser.get_default(key_parts[-1]):
                value = getattr(args, key_parts[-1])
            elif hasattr(args, key) and getattr(args, key) != parser.get_default(key):
                value = getattr(args, key)
            else:
                value = config
                for part in key_parts:
                    if part in value:
                        value = value[part]
                    else:
                        value = default
                        break
            return value
        
        # config        
        self.driver_path = get_arg('driver_path')
        if not os.path.exists(self.driver_path):
            raise ValueError(f"{self.driver_path} not exists")
        self.project_path = get_arg('project_path', '../hibikilogy.github.io')   #本地仓库根路径
        self.upload_url = get_arg('upload_url') #第三方图床
        self.max_retry = get_arg('max_retry',3)
        self.max_timeout = get_arg('max_timeout',10)
        
        self.upload_img = get_arg('upload_img',False)
        self.origin_img = get_arg('origin_img',False)
        self.origin_quality = get_arg('origin_quality',False)
        self.static = get_arg(f'{site}.static',False)
        # self.project_path = os.path.abspath(self.project_path)
        
        self.ids = get_arg(f'{site}.id')
        self.fname = get_arg(f'fname')

        if site=='bili':
            self.is_dyn = get_arg('bili.is_dyn')
