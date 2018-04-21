# -*- coding: utf-8 -*-
'''
Created on 2018年3月1日

@author: ning.lin
设置代理IP
'''
#定义几个全局变量
'''
从http://www.xicidaili.com/获取代理IP，并验证是否能访问爬虫目标网站
如果不能访问，则删除，
'''
#定义几个全局变量
'''
获取网上的代理IP
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
import redis

from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
pool=redis.ConnectionPool(host='192.168.160.132',port=6379,db=0,decode_responses=True)  #427条记录
r = redis.StrictRedis(connection_pool=pool)  

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
            cursor.execute("select ip_port,user_agent from proxy_ip where is_current=1")
            pro_ip = cursor.fetchone()
            cursor.execute('''update proxy_ip set is_current=%s,last_time_use=%s where ip_port=%s''',(1,now_time,pro_ip['ip_port']))
    #         ip = pro_ip['ip_port']
    #         user_agent = pro_ip['user_agent']
    #         print("当前IP为",ip)
    #         print("当前Iuser_agent为",user_agent)
        except Exception as e:
            print("get_proxy_ip报错",str(e))
        finally:
                conn.commit()
                conn.close()
        return pro_ip


def get_random_ip(change_ip):
    conn=connect()
    cursor=conn.cursor()
    print("旧IP超时",change_ip)
    ip_exit = ''
    now_time = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        rand_ip_slq = '''SELECT ip_port,user_agent FROM proxy_ip WHERE validate=1 and ip_port!=%s and id >=((SELECT MAX(id) FROM proxy_ip)-(SELECT MIN(id ) FROM proxy_ip)) * RAND() + (SELECT MIN(id) FROM proxy_ip)  LIMIT 1'''
        cursor.execute(rand_ip_slq,(change_ip,))
        ip_exit = cursor.fetchone()
        print("获取到了新的IP",ip_exit['ip_port'])
        if ip_exit:
           #将当前获取的IPcurrent状态改为1表示当前在使用的IP并且修改当前时间为最近一次使用时间
            cursor.execute('''update proxy_ip set is_current=%s,last_time_use=%s where ip_port=%s''',(1,now_time,ip_exit['ip_port']))
            conn.commit()
            #将之前状态为当前IP的状态改成0（非当前IP）
            cursor.execute("select last_time_use from proxy_ip where ip_port=%s",change_ip)
            conn.commit()
            use_time = cursor.fetchone()['last_time_use']
            print("user_time",use_time)
            startTime= datetime.datetime.strptime(str(use_time),"%Y-%m-%d %H:%M:%S")  
            endTime= datetime.datetime.strptime(str(now_time),"%Y-%m-%d %H:%M:%S")
            seconds = (endTime- startTime).seconds#获取此次与上次时间之差就等于使用了的时间
            cursor.execute('''update proxy_ip set is_current=%s,use_times=%s,validate=%s where ip_port=%s''',(0,seconds,0,change_ip))#修改超时的IP状态
            conn.commit()
            print("IP状态已修改")
            #cursor.execute('''update proxy_ip set is_current=%s,last_time_use=%s where ip_port=%s''',(1,now_time,ip_exit['ip_port']))
        else:
            pass
#                 main()#从网上获取IP并写入数据库中
    except Exception as e:
        print("未找到sql该表可能为空，需要去爬IP",str(e))
#             main()#从网上获
    finally:
        conn.close()
    return ip_exit#返回格式165.227.40.248:3128
# class ProxyIP(object): 
#     proxyList = []
#     f_ip = "D:\\Program Files\\Python_Workspace\\spiders\\p_scrapy\\test_spiders\\test_spiders\\proxy_ip.txt"
#     with open (f_ip,'r') as f:
#         for line in f.readlines():
#             print("line",line)
#             proxyList.append(line)
# #     proxyList = ["122.114.31.177:808"]
#     def process_request(self, request, spider):  
#         # Set the location of the proxy  
#         pro_adr = random.choice(self.proxyList)  
#         print("当前使用的代理IP:" + pro_adr)  
#         request.meta['proxy'] = "http://" + pro_adr  
#RetryMiddleware
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
        r.rpush ('jiayuan_get_noPage',request.url)
        r.save()
        # 只有当proxy_index>fixed_proxy-1时才进行比较, 这样能保证至少本地直连是存在的.
#             if request_proxy_index > self.fixed_proxy - 1 and self.invalid_proxy_flag: # WARNING 直连时超时的话换个代理还是重试? 这是策略问题
#                 if self.proxyes[request_proxy_index]["count"] < self.invalid_proxy_threshold:
#                     self.invalid_proxy(request_proxy_index)
#                 elif request_proxy_index == self.proxy_index:  # 虽然超时，但是如果之前一直很好用，也不设为invalid
#                     self.inc_proxy_index()
        print("当前",self.proxy_ip['ip_port'])
        proxy_ip = get_random_ip(self.proxy_ip['ip_port'])
#         print("换一个代理IP:" + self.proxy_ip['ip_port'])
#         print("换一个代理agent:" + self.proxy_ip['user_agent'])
        request.meta['proxy'] = "http://" + self.proxy_ip['ip_port']
        new_request = request.copy()
        new_request.dont_filter = True
        return new_request
#         return request



