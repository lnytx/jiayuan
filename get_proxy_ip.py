# -*- coding:utf-8 -*-
'''
Created on 2018年2月28日
@author: ning.lin
'''
'''
从http://www.xicidaili.com/获取代理IP，并验证是否能访问爬虫目标网站
如果不能访问，则删除，
'''
#定义几个全局变量

from distutils.command.check import check
from multiprocessing import Pool
import multiprocessing
import os
from queue import Queue
import random
import re
import socket
import threading
import time

from bs4 import BeautifulSoup
import pymysql
import requests
from scrapy.utils.project import get_project_settings




# print("文件为",settings['PROXY_IP_FILE'])
# PROXY_IP_FILE=settings['PROXY_IP_FILE']



user_agent_list = [\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
       ]
#获取随机的header
header={"User-Agent":random.choice(user_agent_list)}
print("hdader",header)
#获取代理IP
lock = threading.Lock()#定义锁，防止重复写文件
q = Queue()#创建先进先出队列，全局中变量
ip={}   #初始化列表用来存储获取到的IP
# url='http://www.xicidaili.com/'
# url = "http://ip.yqie.com/ipproxy.htm"
#     url = "http://ip.seofangfa.com/"
# url = "http://www.66ip.cn/areaindex_19/1.html"
# url = "http://www.ip3366.net/?stype=1&page=4"#可翻页
url = "https://www.kuaidaili.com/free/inha/4/"

# url = 'http://ip.zdaye.com/'
req=requests.get(url=url,headers=header)
req.encoding = 'utf-8' 
r=req.text
soup=BeautifulSoup(r,'html.parser')
# print(soup)
p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')#判断是否为IP
proxy_ip=[]
set_ip = set()#利用set去除文件中重复的IP
ip_list=[]
ip_port=''
# print("soup",soup)
#     iplistn=soup.findAll('tr',class_='')#对应的url='http://www.xicidaili.com/'
# iplistn=soup.findAll('tr',align='center')#url = "http://ip.yqie.com/ipproxy.htm"
if 'www.66ip.cn' in url:
    iplistn=soup.findAll('table',attrs={'bordercolor':'#6699ff'})#url = "http://www.66ip.cn/areaindex_2/1.html"
    for tr in iplistn:
        td = tr.find_all('td')
        for j in range(len(td)):
#             print("j",type(td[j]),td[j].text)
            if p.match(td[j].text):#如果是IP
            #ip_port[ip_list[j]]=ip_list[j+1]
                ip_port = str(td[j].text.strip())+":"+str(td[j+1].text.strip())#119.188.94.145:80这种形式
                set_ip.add(ip_port)
if 'www.xicidaili' in url:
    iplistn=soup.findAll('tr',class_='')
    for i in iplistn:
#         print("i",i)
        ip=i.text.strip().strip()
        ip_list=ip.split()
    for j in range(len(ip_list)):
        if p.match(ip_list[j]):#如果是IP
            #ip_port[ip_list[j]]=ip_list[j+1]
            ip_port = str(ip_list[j].strip())+":"+str(ip_list[j+1].strip())#119.188.94.145:80这种形式
            set_ip.add(ip_port)
    print("iplistn",iplistn)
if 'ip.yqie.com' in url:
    iplistn=soup.findAll('tr',align='center')
    for i in iplistn:
#         print("i",i)
        ip=i.text.strip().strip()
        ip_list=ip.split()
        for j in range(len(ip_list)):
            if p.match(ip_list[j]):#如果是IP
                #ip_port[ip_list[j]]=ip_list[j+1]
                ip_port = str(ip_list[j].strip())+":"+str(ip_list[j+1].strip())#119.188.94.145:80这种形式
                set_ip.add(ip_port)
if 'www.ip3366.net' in url:
    print("soup",soup)
    iplistn=soup.findAll('tr')
    for i in iplistn:
#         print("i",i)
        ip=i.text.strip().strip()
        ip_list=ip.split()
        for j in range(len(ip_list)):
            if p.match(ip_list[j]):#如果是IP
                ip_port = str(ip_list[j].strip())+":"+str(ip_list[j+1].strip())#119.188.94.145:80这种形式
                set_ip.add(ip_port)

if 'www.kuaidaili.com' in url:
    iplistn=soup.findAll('table',class_="table table-bordered table-striped")#url = "http://www.66ip.cn/areaindex_2/1.html"
    print("soup",soup)
    for tr in iplistn:
        td = tr.find_all('td')
        for j in range(len(td)):
            print("j",type(td[j]),td[j].text)
            if p.match(td[j].text):#如果是IP
            #ip_port[ip_list[j]]=ip_list[j+1]
                ip_port = str(td[j].text.strip())+":"+str(td[j+1].text.strip())#119.188.94.145:80这种形式
                set_ip.add(ip_port)
#将set中元素添加到list
for name in set_ip:
    print("name",name)
#     ip["http:"] = name
    proxy_ip.append(name)#将不重复的IP添加到列表中[{'http:','192.1.1.8:808'}]
#使用代理IP访问url


def connect():
    config={'host':'127.0.0.1',
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





def check_url(i):
    '''
    deque['119.188.94.145:80', '113.120.130.249:8080']
    url为网站url
    '''
#     que = get_proxyIP()
    user_agent_list=[
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    #获取随机的header
    header={"User-Agent":random.choice(user_agent_list)}
    #根据上面的方法获取一个随机的代理IP
    #q=get_proxyIP()
    url = "http://www.jiayuan.com/175017527?fxly=pmtq-ss-210&pv.mark=s_p_c|175017527|68209968"
    ip={}
    req = ''
    #获取数据连接
    conn=connect()
    cursor=conn.cursor()
    print("当前验证的IP:",proxy_ip[i])
    
#         ip['http'] = que.get()#从队列中读取爬到的IP
    try:
        req = requests.get(url, proxies={"http":"http://"+proxy_ip[i]}, headers=header)
        print("返回状态码",req.status_code)
        if req.status_code==200:
            try:
                lock.acquire()
                cursor.execute("select ip_port from proxy_ip where ip_port=%s",(proxy_ip[i].strip()))
                ip_exit = cursor.fetchone()
                print("ip_exit",ip_exit)
                if ip_exit:
                    print("执行updata")
                    cursor.execute('''update proxy_ip set ip_port=%s,user_agent=%s where ip_port=%s''',(proxy_ip[i].strip(),str(random.choice(user_agent_list)),proxy_ip[i].strip().strip()))
                else:
                    print("执行insert")
                    cursor.execute("insert into proxy_ip(ip_port,user_agent) value(%s,%s)",(proxy_ip[i].strip().strip(),str(random.choice(user_agent_list))))
                    lock.release()
            except Exception as e:
                print("有异常",str(e))
            finally:
                conn.commit()
        #释放锁218.56.132.154:8080,159.255.163.189:80
#             r=req.text
#             soup=BeautifulSoup(r,'html.parser')
    except Exception as e:
        print("异常",str(e))
    finally:
        pass
    #随机将其中一条数据的当前状态入为0
            #如果不是200就重试，每次递减重试次数,使用函数获取soup数据
                #如果url不存在会抛出ConnectionError错误，这个情况不做重试  
            #return check_url(url,retry-1)
                #req.close()
#当前IP {'http': '42.96.168.79:8888'}
      
#利用set去掉重复的行
def init_proxy_db():
    '''
    将其中任意一条IP的is_current设置为1，作为第一次使用的proxy_ip
    '''
    conn=connect()
    cursor=conn.cursor()
    #去掉IP中的回车与换行
    try:
        cursor.execute('''SELECT ip_port FROM proxy_ip WHERE id >= \
                            ((SELECT MAX(id) FROM proxy_ip)-(SELECT MIN(id ) \
                            FROM proxy_ip)) * RAND() + (SELECT MIN(id) FROM proxy_ip)  LIMIT 1
                    ''')
        curr_ip = cursor.fetchone()['ip_port']
        cursor.execute("UPDATE proxy_ip SET  ip_port = REPLACE(REPLACE(ip_port, CHAR(10), ''), CHAR(13), '')")
        #scrapy代理会始终获取状态为1的IP做为代理IP，直到超时或使用了1个小时,初始时数据库中始终有一个状态为1的IP
        cursor.execute("update proxy_ip SET is_current=1 where ip_port=%s",curr_ip)
    except Exception as e:
        print("异常",str(e))
    conn.commit()
    conn.close()

def main():
#     get_proxyIP()#获取IP，写入临时文件
    
    '''
    多线程
    '''
    thread_list = []    #线程存放列表
    for i in range(len(proxy_ip)):
        t =threading.Thread(target=check_url,args=(i,))
        t.setDaemon(True)
        thread_list.append(t)
        
    for t in thread_list:
        t.start()
        
    for t in thread_list:
        t.join() 
    init_proxy_db()

if __name__=="__main__":
    main()
#     check_url()
