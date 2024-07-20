# Spiders
一系列根据各论坛 / 网站帖子 / 文章 ID 生成指定格式 markdown 文件的爬虫。

目前功能较为完善的网站：
- bilibili.com/opus/
- bilibili.com/read/
- tieba.baidu.com/p/
- bgm.tv/blog/
- zhihu.com/answer/
- zhuanlan.zhihu.com/p/
  
文章可选择生成`jekyll`(默认)或`zola`格式

## 使用方法

### 准备

C++编译环境，[参考](https://stackoverflow.com/questions/64261546/how-to-solve-error-microsoft-visual-c-14-0-or-greater-is-required-when-inst)

安装 Python 并下载本仓库，`pip install -r requirements.txt`安装依赖

下载chrome浏览器版本对应的driver，版本[>=115, 需复制链接下载](https://getwebdriver.com/) | [<114](https://chromedriver.chromium.org/downloads)，修改配置中的driver路径 

将模板配置文件`config.template.json`复制一份重命名为`config.json`, 作为实际使用的配置文件，填入自己的配置

### 两种运行方式：
1. 在本仓库目录输入命令：
    ```bash
    python xxx.py --id id1 id2 ...
    ```
    其中 `xxx.py` 是对应平台的文件名称，`idx` 是帖子 ID，支持前缀+数字(eg.cv123)或只有数字。
    `python xxx.py -h`查看参数帮助
  
2. 修改使用`config.json`中的配置直接运行`xxx.py`
   
   id列表支持前缀+数字字符串和纯数字id
  
默认配置为动态渲染并下载原帖图像到本地webp

爬取b站动态(aka bilibili.com/opus/*)需要设置`is_dyn`为`true`

知乎回答只需输入答案id，专栏/问答通过参数`is_qa`控制

 其他参数详情请查看`python xxx.py -h`或`config.py`文件


## 注意事项
支持两种配置方法：`config.json`以及命令行参数

参数查找顺序为命令行参数传入>config值>命令行参数默认值（config.py）

如需正常使用脚本功能，请确保目录满足以下条件：
```
.
├─hibikilogy.github.io
│  │─images
│  │─temp
│  └─_post
└─spiders（当前目录）
```

文章会生成在`hibikilogy.github.io/temp`，需校验后手动移至`_post`提交。

图片可在本地查看/编辑。在提交到 `hibikilogy.github.io` 时自动转换图片路径。

下载图像文件名为`{hash64}.w{weight}.h{height}.webp`，其中`hash64=urlsafe_b64encode(blurhash(img_bytes))`

`blurhash`参考https://github.com/woltapp/blurhash

## TODO
咕咕咕
- 全局
  - [x] 自动上传图床。
  - [x] 模块化。
  - [x] 当 sm.ms 图床不可用时使用 GitHub 图床。
  - [x] 修改 html2text 使其不自动删除 \<span\> 标签。
  - [x] 将第一幅图自动设置为头图。
  - [ ] NGA 文章内的图片链接会中间换行，咋办？
  - [ ] 面向对象。
- Bilibili
  - [x] 基本功能实现。
- 虎扑
  - [x] 基本功能实现。
- NGA
  - [x] 基本功能实现。
  - [ ] 修复只能找到 UID 的问题。
- S1
  - [x] 基本功能实现。
- 贴吧
  - [x] 基本功能实现。
  - [ ] <del>修复日期有时变成“一楼”的问题。</del>似乎暂无可靠的方法。

## 已知问题
- 图床 sm.ms 限制每个 IP 一小时上传 100 张图片（如果上传太频繁似乎会变成每周 50 张）。

## 如何贡献
只要功能 OK 代码可观性高就行了。

## 感谢
- [sm.ms](https://sm.ms) 图床。
- [jsDelivr](https://www.jsdelivr.com/) 的免费 CDN 服务。