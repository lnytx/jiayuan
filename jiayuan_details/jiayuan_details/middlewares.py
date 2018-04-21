# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class jiayuan_next_pageSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class jiayuan_next_pageDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

import re

import redis
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pymysql

from jiayuan_details.settings import USER_NAME, PASSWD
global driver
global r

login_url = 'http://login.jiayuan.com/'#登录时的url
option = webdriver.ChromeOptions()
prefs={"profile.managed_default_content_settings.images":2}#禁止加载图片
option.add_experimental_option("prefs",prefs)
option.add_argument('--headless')
option.add_argument("--window-size=1920,1080")
# option.add_argument(pro_ip['user_agent'])#自定ageng
# option.add_argument('--proxy-server=http://'+pro_ip['ip_port'])
# option.add_argument("--proxy-server=http://222.73.68.144:8090")
pool=redis.ConnectionPool(host='192.168.160.132',port=6379,db=0,decode_responses=True)  #427条记录
r = redis.StrictRedis(connection_pool=pool)  
redis_pipe = r.pipeline()
print("登录中",USER_NAME)
try:
    driver = webdriver.Chrome(chrome_options=option)
    driver.get(login_url)#登录页面
#     print(driver.page_source)
    import time
    time.sleep(10)#一定要登录，后面才能取到下一页的标签，如果没有的话会有一个框挡住，导致无法获取下一页标签
#     driver.find_element_by_id("login_btn").click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID,'login_btn'))).click()
    driver.find_element_by_id("login_email").clear()
    driver.find_element_by_id("login_email").send_keys(USER_NAME) #修改为自己的用户名
    driver.find_element_by_id("login_password").clear()
    driver.find_element_by_id("login_password").send_keys(PASSWD) #修改为自己的密码
    #登录url
    #url="http://login.jiayuan.com/"
#     driver.find_element_by_id("login_btn").click()#点击登录按钮
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID,'login_btn'))).click()
    #登录url
    #url="http://login.jiayuan.com/"
#     driver.find_element_by_id("login_btn").click()#点击登录按钮
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'login_btn'))).click()
    driver.implicitly_wait(3)
    time.sleep(10)
    title = driver.title;
    print("页面的title",type(title),title)
    if title =='佳缘登录页_世纪佳缘交友网':
        print("已成功登录执行了页面")
        driver.save_screenshot('登录成功时.png')
except Exception as e:
    driver.close()
    print("spider出现了异常,关闭",str(e))
        
#         print("已登录",driver.page_source)
class SeleniumMiddleware(object):
    def process_request(self, request, spider):
        
        '''
        自己定义一个方法，用来解析元素
        '''
        
        #         if request.meta.has_key('PhantomJS'): #当请求经过下载器中间件时,检查请求中是否有这个meta,决定这个请求要不要使用中间件。
#             driver = webdriver.PhantomJS() 
#             driver.get(request.url) 
#             content = driver.page_source.encode('utf-8') 
#             driver.quit() 
#             return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
        global driver
        global r
        #根据url判断是详情页面还是人员列表页
        main = 'http://search.jiayuan.com/v2/index.php?key=&sex=f&stc=&sn=default&sv=1&p='
        deatils = 'http://www.jiayuan.com/\d+'
        user_list=''
        if re.findall(deatils,request.url):
            print("传入的是人员详情url，返回人员页面",request.url)
            '''
                                    一定要支请求人员低页面，这里如果是无效的页面的话会返回http://www.jiayuan.com/blacklist.php?uid=100000938，没有这行是不会返回blacklist的
            '''
            driver.get(request.url)
            html_source = driver.page_source
#             html_source = driver.page_source
#             if '查看用户详细资料失败' in html_source:
#                 print("该%s是无效的url",request.url)
# #                 r.sadd ('jiayuan_faile',request.url)
#                 r.rpush ('jiayuan_faile',request.url)
#                 r.save()
#                 return None
#             else:
# #                 r.sadd ('jiayuan_url',request.url)
#                 r.rpush ('jiayuan_url',request.url)
#                 r.save()
            return HtmlResponse(url=driver.current_url,body=html_source,
                    encoding="utf-8", request=request)
    def closed(self,spider):
        print("spider closed")
        driver.close()