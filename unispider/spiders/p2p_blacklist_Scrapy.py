#coding:utf-8

"""
  从贷联盟上爬取网贷黑名单详细信息的url
  author: 邓友辉
  email:heshang1203@sina.com
  date:2015/06/10
"""
from scrapy.utils.request import request_fingerprint
from scrapy.spider import Spider
from scrapy.http import Request
from scrapy import log
from scrapy import signals
import time

from unispider.items import *

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class p2pBlacklist(Spider):
    download_delay=1
    name = 'dailm'
    start_urls = ['http://www.dailianmeng.com/p2pblacklist/index.html']
    allowed_domains = ['dailianmeng.com']
    # writeInFile = "/home/dyh/data/specialworker/judicial/url_j.txt"
    writeInFile = "E:/DLdata/dailm.txt"
    # haveRequested = "/home/dyh/data/specialworker/judicial/haveRequestedUrl.txt"
    haveRequested = "E:/DLdata/dailm_control.txt"
    order = range(1, 17)
    def __inti__(self):
        pass

    def set_crawler(self,crawler):
        super(p2pBlacklist, self).set_crawler(crawler)
        self.bind_signal()


    def bind_signal(self):
        self.crawler.signals.connect(self.open_file, \
            signal=signals.spider_opened)  #爬虫开启时，打开文件
        self.crawler.signals.connect(self.close_file, \
            signal=signals.spider_closed)  #爬虫关闭时，关闭文件

    def open_file(self):
        self.file_handler = open(self.writeInFile, "a")  #写内容
        self.file_haveRequested = open(self.haveRequested, "a+")  #写入已请求成功的url
        self.url_have_seen = set()
        for line in self.file_haveRequested:
            fp = self.url_fingerprint(line)
            self.url_have_seen.add(fp)


    def close_file(self):
        self.file_handler.close()            

    def url_fingerprint(self, url):
        req = Request(url.strip())
        fp = request_fingerprint(req)
        return fp             

    def make_requests_from_url(self, url):
        return Request(url, callback=self.gettotal, dont_filter=True)

    def gettotal(self, response):
        """
        extract pages from different years
        """
        sel = response.selector
        total_pages = sel.xpath(u"//a[contains(text(),'末页')]\
            /@href").re(u"page=([\d]*)")
        url = 'http://www.dailianmeng.com/p2pblacklist/index.html?P2pBlacklist_page='
        urls = [url+str(page) for page in xrange(1,(int(total_pages[0])+1))]
        for url in urls[0:1]:
            # print url, "year url"
            yield Request(url, callback=self.detail_url, dont_filter=True)

    def detail_url(self, response):
        """
        extract url for detail information and store it into 
        redis
        """
        sel = response.selector
        detail_url = sel.xpath(u"//a[contains(text(),'查看详情')]/@href").extract()
        url = 'http://www.dailianmeng.com'
        urls = [url+i for i in detail_url]
        for url in urls:
            fp = self.url_fingerprint(url)
            if fp not in self.url_have_seen:
                self.url_have_seen.add(fp)
                yield Request(url, 
                    callback = self.detail, dont_filter=False)
            else:
                pass

    def detail(self, response):
        """
        extract detail info and store it in items
        """
        item = UnispiderItem()
        sel = response.selector
        self.file_haveRequested.write(response.url+"\n")
        try:
            info = []
            for i in self.order:
                xpath_sen = "//table[@id='yw0']/tr[%s]/td/text()"%str(i)
                tmp_con = sel.xpath(xpath_sen).extract()
                tmp_con = self.for_ominated_data(tmp_con)
                info.append(tmp_con)
        except Exception,e:
            log.msg("error_info==%s"%e, level=log.ERROR)

        try:
            info.append(str(time.strftime("%Y年%m月%d日")))
            info = '\001'.join(info)+"\n"
            item['content'] = info
            yield item
        except Exception, e:
            log.msg('ERROR_info:{e} final:{url},item content=={content}'.format(url=response.url,\
                content = '\001'.join(info)+"\n", e=e),\
                level=log.ERROR)


    def for_ominated_data(self,i_list):
        """
        some elements are ominated, set the ominated elements
        as "" 
        """
        try:
            if len(i_list) == 0:
                i_list.append("")
            else:
                pass
            assert len(i_list) == 1, "the element must be unique"
            return i_list[0]
        except Exception, e:
            log.msg(e, level=log.ERROR)