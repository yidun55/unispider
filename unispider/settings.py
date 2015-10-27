# -*- coding: utf-8 -*-

# Scrapy settings for unispider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'unispider'

SPIDER_MODULES = ['unispider.spiders']
NEWSPIDER_MODULE = 'unispider.spiders'

DEFAULT_ITEM_CLASS = 'unispider.items.UnispiderItem'
ITEM_PIPELINES = ['unispider.pipelines.UnispiderPipeline']

# LOG_FILE = '/home/dyh/data/mobile/log'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'unispider (+http://www.yourdomain.com)'
