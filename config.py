# 爬虫参数&配置文件
import argparse, os, json

class CrawlerConfig():
    # 参数查找顺序：命令行参数传入>config.json值>命令行参数默认值
    def __init__(self, config_file, site):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        parser = argparse.ArgumentParser()
        parser.add_argument("--static","-s", action="store_true", default=False, help="Whether to use static mode(simpler & faster but easy to be banned), default False")
        parser.add_argument("--driver_path", type=str, default="chromedriver.exe", help="Path to chrome driver")
        parser.add_argument("--id","-id", nargs='+', type=str, default=[], help="List of post ids")
        parser.add_argument("--fname","-n", nargs='+', type=str, default=[], help="List of post custom file names")
        parser.add_argument("--front","-fn", type=str, choices=["jekyll","zola"], default="jekyll", help="Witch front to generate, default jekyll")
        parser.add_argument("--ua.platforms","-u.p", type=str, choices=["pc", "mobile", "tablet"], default="pc", help="Which platform for user-agent, default pc")
        parser.add_argument("--ua.os","-u.o", type=str, choices=["windows", "macos", "linux"], default="windows", help="Which os for user-agent, default windows")
        #img
        parser.add_argument("--upload_img","-u", action="store_true", default=False, help="Whether to upload imgs via third-party img hosting service, please change your upload_url in config, default False")
        parser.add_argument("--origin_img","-o", action="store_true", default=False, help="Whether to use original img url directly, default False")
        parser.add_argument("--size_thr","-t", type=int, default=85, help="Size threshold in kB for not compressing images, '-1' means original quality")
        parser.add_argument("--format","-fm", type=str, default="webp", help="Image saving format, default webp")
        if site=='bili':
            parser.add_argument("--bili.is_dyn","-b.d", action="store_true", default=False, help="Take ids as bilibili dynamic post")
        if site=='zhihu':
            parser.add_argument("--zhihu.is_qa","-z.q", action="store_true", default=False, help="Take ids as zhihu qustion & anwser")
        
        args = parser.parse_args()
        def arg_overwrite(key, value):
            if hasattr(args, key) and \
                (getattr(args, key) != parser.get_default(key) or value==None):
                value = getattr(args, key)
            return value
        def get_arg(key,default = None):
            key_parts = key.split('.')
            value = config
            for part in key_parts:
                if part in value:
                    value = value[part]
                else:
                    value = default
                    break
            value = arg_overwrite(key_parts[-1], value)
            value = arg_overwrite(key, value)
            if value==None:
                raise ValueError(f"param {key} not found, please check the config")
            return value
        
        # config        
        self.driver_path = get_arg('driver_path')
        if not os.path.exists(self.driver_path):
            raise ValueError(f"{self.driver_path} not exists")
        self.project_path = get_arg('project_path', '../hibikilogy.github.io')   #本地仓库根路径
        self.upload_url = get_arg('upload_url') #第三方图床
        self.max_retry = get_arg('max_retry',3)
        self.max_timeout = get_arg('max_timeout',10)
        self.front = get_arg('front')
        
        self.upload_img = get_arg('upload_img',False)
        self.origin_img = get_arg('origin_img',False)
        self.size_thr = get_arg('size_thr')
        self.format = get_arg('format')
        self.static = get_arg(f'{site}.static',False)
        self.ua = get_arg(f'ua')
        # self.project_path = os.path.abspath(self.project_path)
        
        self.ids = get_arg(f'{site}.id')
        self.fname = get_arg(f'fname')

        if site=='bili':
            self.is_dyn = get_arg('bili.is_dyn')
        if site=='zhihu':
            self.ua = get_arg('zhihu.ua')
            self.is_qa = get_arg('zhihu.is_qa')

        self.ua["platforms"] = arg_overwrite("ua.platforms", self.ua["platforms"])
        self.ua["os"] = arg_overwrite("ua.os", self.ua["os"])