# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class TiebaSpiderPipeline(object):
    def process_item(self, item, spider):
        with open(f'{item["date"]}-{item["title"]}.md', 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write('layout: post\n')
            f.write(f'title: {item["title"]}\n')
            f.write(f'author: {item["author"]}\n')
            f.write(f'original: {item["url"]}\n')
            f.write(f'catalog: true\n')
            f.write('---\n')
            f.write(item['content'])
        return item
