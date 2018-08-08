# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class BbcSpiderPipeline(object):
    def process_item(self, item, spider):
        with open("wiktionary_es_verbs.txt", 'ab+') as fp:
            fp.write(item["word"] + b"\t" + item['languages'] + b'\n')
