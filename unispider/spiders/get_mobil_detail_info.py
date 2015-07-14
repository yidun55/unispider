#!usr/bin/env python
#encoding: utf-8


from scrapy import Spider
from scrapy import Request
from scrapy import log
from unispider.items import *
import HTMLParser

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def for_ominated_data(info_list, xpath_list):
    """
    for some ominated data
    """
    if len(xpath_list) == 0:
        xpath_list.append("")
        log.msg("error for_ominated_data log_message=%s"%'\001'.join(info_list),level=log.ERROR)
    else:
        pass
    try:
        assert len(xpath_list) >= 1, 'xpath_list must be one element'
        xpath_list = [el.strip() for el in xpath_list]
        info_list.extend(xpath_list)
    except Exception, e:
        log.msg(log_message="for_ominated {info}".format(info=e),level=log.ERROR)
    return info_list


class UniSpider(Spider):
    """
    应老马的要求，爬取电话号码的详细信息
    """
    name = 'mobile'
    download_delay = 1
    start_urls = ["http://www.iplaypython.com"]
    handle_httpstatus_all = True
    def __init__(self):
        self.path = '/home/dyh/spiders/mobileDetail/norecord_mobile_code.txt'
        self.f = open(self.path, "r")
        self.url_shouji = 'http://shouji.supfree.net/fish.asp?cat=%s'
        self.url_ip138 = 'http://www.ip138.com:8080/search.asp?mobile=%s&action=mobile'

    def parse(self, response):
        """
        忽略初始的response
        """
        for num in self.f.readlines():
            url = self.url_shouji%str(num.strip())
            yield Request(url,callback=self.shouji_parse, dont_filter=True,meta={"num":num})

    def shouji_parse(self, response):
        """
        解析手机网上的信息
        """
        detail_list = []
        detail_list.append(response.meta["num"].strip())
        try:
            assert response.status == 200, "error in shouji_parse assert"
            sel = response.selector
            classi = sel.xpath(u"//span[text()='卡类型：']/../text()").extract()
            detail_list = for_ominated_data(detail_list, classi)
            bus = sel.xpath(u"//span[text()='运营商：']/following-sibling::a[1]/text()").extract() #运营商
            detail_list = for_ominated_data(detail_list,bus)
            #从shouji上完数据提取后，开始从ip138上提取数据，并且将shouji上的数据传给下一个解析函数
            num = response.meta['num'].strip()
            url = self.url_ip138%str(num)
            yield Request(url, callback=self.ip138_parse,dont_filter=True,meta={"num":num,'detail_list':detail_list})
        except  Exception,e:
            log.msg("error undownload mobile num=%s,error_info=%s"%(response.meta["num"].strip(),e),level=log.ERROR)

    def ip138_parse(self, response):
        """
        解析ip138上的信息
        """
        detail_list = response.meta["detail_list"]
        num = response.meta["num"]
        item = UnispiderItem() 
        try:
            assert response.status == 200, "error in ip138_parse assert"
            sel = response.selector
            district_code = sel.xpath(u"//td[text()='区 号']/following-sibling::td[1]/text()").extract()
            detail_list = for_ominated_data(detail_list,district_code)   #区号
            fox_code = sel.xpath(u"//td[text()='邮 编']/following-sibling::td[1]/text()").extract()
            detail_list = for_ominated_data(detail_list,fox_code)   #邮编
            local = sel.xpath(u"//td[text()='卡号归属地']/following-sibling::td[1]/text()").extract()
            html_parse = HTMLParser.HTMLParser()
            #local = html_parse.unescape(local)  #解析html中的空格
            try:
                local = local[0].strip()
                local = local.split(html_parse.unescape("&nbsp;")) #应老马要求将归属地拆开
            except Exception,e:
                log.msg("归属地_errror %"%"|".join(detail_list),level=log.ERROR) 
            detail_list = for_ominated_data(detail_list, local)#卡号归属地
            try:
                item["content"] = "|".join(detail_list)
                yield item
            except Exception,e:
                log.msg("error detail_list join num=%s, info=%s" %(num, "\001".join(detail_list)))

        except  Exception,e:
            log.msg("error undownload mobile num=%s, error_info=%s"%(num, e), level=log.ERROR)


