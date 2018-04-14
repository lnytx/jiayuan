# -*- coding:utf-8 -*-
'''
Created on 2018年2月28日
@author: ning.lin
'''
'''
大图地址class或id有big字样 的
<div class="pho_big" id="phoBig" style="height: 640px;">
<div class="big_pic fn-clear" id="bigImg">
小图地址
<div class="pho_small_box fn-clear mt25 " id="phoSmallPic">
'''

'''
拼接url，佳缘人员ID为9位数，第一步是先将有人员信息的数据提取出来，
1到999999999
'''

import json
import time

import redis   
from scrapy  import log
from scrapy import cmdline
import scrapy
from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy_redis.spiders import RedisSpider
from selenium import webdriver


from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from create_jiayuan_urls.items import UrlItem
from create_jiayuan_urls.settings import USER_NAME, PASSWD
import re

class jiayuan_data(RedisSpider):
    pool=redis.ConnectionPool(host='127.0.0.1',port=6379,db=0,decode_responses=True)  #427条记录
    r = redis.StrictRedis(connection_pool=pool)  
    redis_pipe = r.pipeline()
#     allowed_domains = ["jiayuan.com"]
    name = "jiayuan_last"
    
    redis_key = 'jiayuan_last:start_urls'
#     url_base = 'http://search.jiayuan.com/v2/index.php?key=&sex=f&stc=&sn=default&sv=1&p=%s&pt=163649&ft=off&f=select&mt=d'
    start_urls = []
    '''
        在中间件中将正确的页面写入redis中，注意要在中间件修改redis的路径，这个spider一般在docker中运行，向redis中传递详情url
    '''
    
    def start_requests(self):#
        for p in range(100000000,999999999):
            url = "http://www.jiayuan.com/%s" %(p)
            yield Request(url=url)
#             yield Request(url=url,callback=self.get_main_info)
    def get_main_info(self,response):
#         url_main = response.body.decode('utf-8')
#         print("从中间件传来的body页面",type(url_main),url_main)
        print("当前返回的url",response.url)
        re_str = 'blacklist.php?uid'#无效的url
        deatils = 'http://www.jiayuan.com/\d+'
        if re_str in response.url:#http://www.jiayuan.com/blacklist.php?uid=100000938，说明是无效的url
            print("失败的url",response.url)
            self.r.rpush ('jiayuan_failed',response.url)
            self.r.save()
        elif  re.findall(deatils,response.url):
            item = UrlItem()
            item['url'] = response.url
            yield  item
cmdline.execute("scrapy crawl jiayuan_last".split())