# Spiders
一系列根据各论坛 / 网站帖子 / 文章 ID 生成指定格式 markdown 文件的爬虫。

目前功能较为完善的网站：
- 贴吧
- 虎扑
- bilibili
- NGA
- Stage1

## 使用方法
安装 Python 并下载本仓库，在仓库目录输入命令如下：
```shell
python xxx.py id
```
其中 `xxx.py` 是对应平台的文件名称，`id` 是帖子 ID。

## 注意事项
如需正常使用以 GitHub 作为图床的功能，请确保目录满足以下条件：
```
.
├─hibikilogy.github.io
│  └─images
└─spiders（当前目录）
```
图片需要提交 `hibikilogy.github.io` 内的更改后方可查看。如果有更好的解决方法，欢迎贡献。

## TODO
咕咕咕
- 全局
  - [x] 自动上传图床。
  - [x] 模块化。
  - [x] 当 sm.ms 图床不可用时使用 GitHub 图床。
  - [ ] 修改 html2text 使其不自动删除 \<span\> 标签，目前似乎并不完善。
  - [x] 将第一幅图自动设置为头图。
  - [ ] 面向对象。
- Bilibili
  - [x] 基本功能实现。
- 虎扑
  - [x] 基本功能实现。
- NGA
  - [x] 基本功能实现。
  - [ ] 修复只能找到 UID 的问题（Firefox）。
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