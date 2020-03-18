# Spiders
一系列根据各论坛 / 网站帖子 / 文章 ID 生成指定格式 markdown 文件的爬虫。自行修改格式可以做到快捷转载文章到使用 markdown 的博客。

目前功能较为完善的网站：
- 贴吧
- 虎扑
- bilibili

## 使用方法
运行 .py 文件，根据命令行提示输入帖子 / 文章 ID。

对于 Windows 系统，需要事先安装好 Python。


## TODO
咕咕咕
- 全局
  - [x] 自动上传图床。
  - [x] 可能需要把每个爬虫都用的功能整合为模块。
  - [ ] 将第一幅图自动设置为头图。
  - [ ] 可能需要面向对象。
  - [ ] 可以试试看装载到网站上在线使用。
- Bilibili
  - [x] 基本功能实现。
- 虎扑
  - [x] 基本功能实现。
- NGA
  - [ ] 基本功能实现（可能需要自己写一个完善的 bbcode2markdown）。
- S1
  - [x] 基本功能实现。
  - [ ] 修复附件形式的图片无法正确显示的问题。
- 贴吧
  - [x] 基本功能实现。
  - [ ] 修复日期有时变成“一楼”的问题。

## 已知问题
- 图床 sm.ms 限制每个 IP 一小时上传 100 张图片。
- 最近图床上传貌似不稳定，不知道有什么其他好用的图床做备用。

## 如何贡献
只要功能 OK 代码可观性高就行了。

## 感谢
[sm.ms](https://sm.ms) 图床。请善待这个良心图床。