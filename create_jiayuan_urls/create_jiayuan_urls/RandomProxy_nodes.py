# -*- coding: utf-8 -*-
'''
Created on 2018年3月1日

@author: ning.lin
设置代理IP
'''
'''
多节点跑时使用用这个proxy中间件
'''

import datetime
from distutils.command.check import check
from multiprocessing import Pool
import multiprocessing
import os
from queue import Queue
import random
import random
import random
import re
import socket
import threading
import time
import time

from bs4 import BeautifulSoup
import pymysql
import pymysql
import requests
from scrapy.utils.project import get_project_settings

import datetime


from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError


settings = get_project_settings()





#使用代理IP访问url





'''
在中间件中获取代理IP
'''

def connect():
        config={'host':'192.168.160.132',
                    'user':'root',
                    'password':'root',
                    'port':3306,
                    'database':'jiayuan',
                    'charset':'utf8',
                    #要加上下面一行返回的是list，否则默认返回的是tuple
                    'cursorclass':pymysql.cursors.DictCursor,
                }
        try:
            conn=pymysql.connect(**config)
            print("conn is success!")
            return conn
        except Exception as e:
            print("conn is fails{}".format(e))       

def get_proxy_ip():
        '''
        scrapy通过些函数获取is_current状态为1的IP为代理IP，防止一次request换一次IP（因为登录情况下不可能出现这种情况）
        '''
        conn=connect()
        cursor=conn.cursor()
        now_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            '''
            集群使用时不管是超时还是什么，直接获取一个随机IP，防止多个node同时使用一个IP
            '''
            rand_ip_slq = '''SELECT ip_port,user_agent FROM proxy_ip WHERE validate=1 and id >=((SELECT MAX(id) FROM proxy_ip)-(SELECT MIN(id ) FROM proxy_ip)) * RAND() + (SELECT MIN(id) FROM proxy_ip)  LIMIT 1'''
            cursor.execute(rand_ip_slq)
            pro_ip = cursor.fetchone()
        except Exception as e:
            print("get_proxy_ip报错",str(e))
        finally:
            conn.commit()
            conn.close()
        return pro_ip

'''
代理中间件
'''
class ProxyIP(object):
    '''
    https://github.com/kohn/HttpProxyMiddleware/blob/master/fetch_free_proxyes.py
    '''
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)
    
    # 遇到这些类型的错误直接当做代理不可用处理掉, 不再传给retrymiddleware
    def __init__(self):
    # 是否在超时的情况下禁用代理
#     proxyList = ["122.114.31.177:808"]
        self.proxy_ip = ""
    def process_request(self, request, spider):  
        # Set the location of the proxy  
        print("从数据库获取新的IP")
        i = datetime.datetime.now()#获取当前时间
#         if i.minute % 10 ==0:#每10分钟换一次IP，中间间隔60秒
#             self.proxy_ip = get_proxy_ip()
#             time.sleep(60)
        self.proxy_ip = get_proxy_ip()
        print("当前使用的代理IP:" + self.proxy_ip['ip_port'])
        print("当前使用的代理agent:" + self.proxy_ip['user_agent'])
        request.headers.setdefault('User-Agent', self.proxy_ip['user_agent'])  
        request.meta['proxy'] = "http://" + self.proxy_ip['ip_port']
        
    def process_exception(self, request, exception, spider):
        """
            处理由于使用代理导致的连接异常
        """
#         request_proxy_index = request.meta["proxy_index"]
        print('访问失败%s，出现异常%s' % (request.url, str(exception)))
        # 只有当proxy_index>fixed_proxy-1时才进行比较, 这样能保证至少本地直连是存在的.
#             if request_proxy_index > self.fixed_proxy - 1 and self.invalid_proxy_flag: # WARNING 直连时超时的话换个代理还是重试? 这是策略问题
#                 if self.proxyes[request_proxy_index]["count"] < self.invalid_proxy_threshold:
#                     self.invalid_proxy(request_proxy_index)
#                 elif request_proxy_index == self.proxy_index:  # 虽然超时，但是如果之前一直很好用，也不设为invalid
#                     self.inc_proxy_index()
        print("当前",self.proxy_ip['ip_port'])
        proxy_ip = get_proxy_ip()#不考虑状态，直接取随机IP
#         print("换一个代理IP:" + self.proxy_ip['ip_port'])
#         print("换一个代理agent:" + self.proxy_ip['user_agent'])
        request.meta['proxy'] = "http://" + self.proxy_ip['ip_port']
        new_request = request.copy()
        new_request.dont_filter = True
        return new_request
#         return request



