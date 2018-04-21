# -*- coding: utf-8 -*-
'''
Created on 2018年3月1日

@author: ning.lin
添加随机的一些useragent
'''
import random

import pymysql
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware  


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


class UserAgent(UserAgentMiddleware):
    def process_request(self, request, spider):
        conn=connect()
        cursor=conn.cursor()
        url = request.meta['proxy']#http//:110.52.8.82:53281
        ip = url[url.rfind('/')+1:]
        cursor.execute("select user_agent from proxy_ip where ip_port=%s",(ip,))
        agent = cursor.fetchone()
        print("从proxy_ip中获取的ip为",ip)
        print("从proxy_ip中获取的ip为",agent)
        ua = agent['user_agent']
        if ua:  
            #显示当前使用的useragent  
            #print "********Current UserAgent:%s************" %ua  
            #记录 
            print("当前使用的agent",ua) 
            print("当前的url",request.url)
            request.headers.setdefault('User-Agent', ua)  
        cursor.close()