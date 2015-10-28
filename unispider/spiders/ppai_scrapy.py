#coding:utf-8

"""
  从拍拍贷上爬取网贷黑名单
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
    download_delay=2
    name = 'pplist'
    start_urls = ['http://www.ppdai.com/blacklist/2015']
    allowed_domains = ['ppdai.com']
    # writeInFile = "/home/dyh/data/specialworker/judicial/url_j.txt"
    writeInFile = "E:/DLdata/ppai.txt"
    # haveRequested = "/home/dyh/data/specialworker/judicial/haveRequestedUrl.txt"
    haveRequested = "E:/DLdata/ppai_control.txt"
    def __init__(self):
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
        url = 'http://www.ppdai.com/blacklist/'
        years = xrange(2008,2016)
        urls = [url+str(year) for year in years]
        for url in urls[0:5]:
            # print url, "year url"
            yield Request(url, callback=self.extract, dont_filter=True)

    def extract(self, response):
        """
        extract pages and then Request those pages sequecely
        """
        # print response.url,"extract response url"
        sel = response.selector
        pages = []
        try:
            # print "pages work"
            pages = sel.xpath("//div[contains(@class,'fen_ye_nav')]//td/text()").re(u"共([\d]{1,3})页")
            # print pages
        except Exception, e:
            print e,"error pages"
            log.msg(e, level=log.ERROR)
            log.msg(response.url, level=log.ERROR)

        if len(pages) == 0:
            self.getUserName(response)  #only one page
        else:
            for page in range(int(pages[0])+1)[1:2]: #fro test
                url = response.url+"_m0_p"+str(page)
                yield Request(url, callback=self.getUserName,dont_filter=True)

    def getUserName(self, response):
        """
        get user name from xtml
        """
        sel = response.selector
        blackTr = sel.xpath(u"//table[contains(@class,'black_table')]/tr[position()>1]//p[contains(text(),'真实姓名')]/a/@href").extract()
        url = 'http://www.ppdai.com'
        urls = [url+i for i in blackTr]
        for url in urls[0:1]:
            fp = self.url_fingerprint(url)
            if fp not in self.url_have_seen:
                self.url_have_seen.add(fp)
                yield Request(url, 
                    callback = self.detail, dont_filter=False)
            else:
                pass

    def for_ominated_data(self,info_list,i_list):
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
            info_list.append(i_list[0].strip())
            # print 'you work'
            return info_list
        except Exception, e:
            print 'i work'
            log.msg(e, level=log.ERROR)


    def detail(self, response):
        """
        extract detail info and store it in items
        """
        item = UnispiderItem()
        sel = response.selector
        self.file_haveRequested.write(response.url+"\n")
        total = sel.xpath(u"count(//div[@class='table_nav']\
            //tr)").extract()   #借款的笔数
        total = int(total[0][0])
        for trI in xrange(2, total+1):
            """
            有的用户有多笔的借款
            trI是不同笔借款所在表格的行数
            """
            info = []
            accPri = sel.xpath(u"//table[contains(@class, \
                'detail_table')]/tr[1]/td[1]/text()").re(ur"累计借入本金：([\S\s]*)")    #累计借入本金
            info = self.for_ominated_data(info, accPri)
            ovDate =  sel.xpath(u"//table[contains(@class, 'detail_table')]/tr[1]/td[2]/span/text()").extract()   #最大逾期天数
            info = self.for_ominated_data(info, ovDate)
            bef = u"//table[contains(@class, 'detail_table')]/tr[3]//tr["
            aft = u"]/td[1]/text()"
            ass = bef + str(trI) + aft
            liID   =  sel.xpath(ass).extract()   #列表编号
            info = self.for_ominated_data(info, liID)
            bef = u"//table[contains(@class, 'detail_table')]/tr[3]//tr["
            aft = u"]/td[2]/text()"
            ass = bef + str(trI) + aft
            loNu   =   sel.xpath(ass).extract()  #借款期数
            info = self.for_ominated_data(info, loNu)
            bef = u"//table[contains(@class, 'detail_table')]/tr[3]//tr["
            aft = u"]/td[3]/text()"
            ass = bef + str(trI) + aft
            loTime =  sel.xpath(ass).extract()   #借款时间
            info = self.for_ominated_data(info, loTime)
            bef = u"//table[contains(@class, 'detail_table')]/tr[3]//tr["
            aft = u"]/td[4]/text()"
            ass = bef + str(trI) + aft
            ovDayNu =  sel.xpath(ass).extract()   #逾期天数
            info = self.for_ominated_data(info, ovDayNu)
            bef = u"//table[contains(@class, 'detail_table')]/tr[3]//tr["
            aft = u"]/td[5]/text()"
            ass = bef + str(trI) + aft
            ovPri   =   sel.xpath(ass).extract()  #逾期本息
            info = self.for_ominated_data(info, ovPri)
            prov   = sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li//strong/text()").re(ur"_([\w]*?)_[男|女]")     #省
            info = self.for_ominated_data(info, prov)
            usrNa  =  sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li").re(ur"用户名：([\w\W]*?)\n")    #用户名
            info = self.for_ominated_data(info, usrNa)
            name   =  sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li").re(ur"姓名：([\w\W]*?)\n")    #姓名
            info = self.for_ominated_data(info, name)
            phoneN =  sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li").re(ur"手机号：([\w\W]*?)\n")    #手机号
            info = self.for_ominated_data(info, phoneN)
            ID     =   sel.xpath(u"//div[contains(@class,\
            'blacklist_detail_nav')]//li").re(ur"身份证号：([\w\W]*?)\n")   #身份证号
            info = self.for_ominated_data(info, ID)

            try:
                info.append(str(time.strftime("%Y年%m月%d日")))
                info = '\001'.join(info)+"\n"
                item['content'] = info
                yield item
            except Exception, e:
                log.msg('ERROR:{url}'.format(url=response.url),\
                    level=log.ERROR)