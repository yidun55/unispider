# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
import os
# os.chdir("/home/dyh/data/mobile")

class UnispiderPipeline(object):
    def process_item(self, item, spider):
        # try:
        #     with open("detail_norecord_mobile_num.txt","a") as f:
        #         f.write(item["content"]+"\n")
        # except Exception,e:
        #     log.msg("error pipeline,error_info=%s"%e, level=log.ERROR)
        spider.file_handler.write(item['content'])

