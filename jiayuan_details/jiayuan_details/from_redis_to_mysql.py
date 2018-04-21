# -*- coding:utf-8 -*-
'''
Created on 2018年2月28日
@author: ning.lin
'''
'''
从redis读取详细的item在这里进行格式化之后将数据写入mysql，并且根据item中的image的地址下载图片
'''

import json
import os
import random
import re

import pymysql
import redis  
import requests
import time
import urllib.parse
from settings import IMAGES_STORE

pool=redis.ConnectionPool(host='192.168.160.32',port=6379,db=0,decode_responses=True)  #427条记录
r = redis.StrictRedis(connection_pool=pool)  
redis_pipe = r.pipeline() 



def parse1(list1):
    '''
    将['学历：本科', '身高：160cm', '购车：暂未购车', '月薪：2000～5000元', '住房：与父母同住', '体重：55公斤', '星座：天蝎座', '民族：汉族', '属相：羊', '血型：AB型']
    转成dict{'学历':'本科'}
    '''
    
    result = {}
    temp=[]
    result_str=''
#             temp_dict=[]#result_dict这是因为有些项目下面有多个标签，多个标签就需要合并起来
#             result_dict = {}#多个dict合并后的结果
    if len(list1)>1:#大于1说明该项下有值，否则此项未填信息
        for item in list1:
            temp = item.split('：')#拆分item
            result[temp[0]] = temp[1]
#             temp.append(result)
        return result
    else:
        return list1
    #其他则返回str
def parse2(str1):
    '''
    将['月薪：', '2000～5000元', '购房：', '--', '购车：', '--', '经济观念：', '--', '投资理财：', '--', '外债贷款：', '--']
    这种情况转成dict{'月薪':'2000～5000元','购房：':'--'}
    '''
    temp_list = str1.split(';')
    result={}
    result_str=''
#             temp_dict=[]#result_dict这是因为有些项目下面有多个标签，多个标签就需要合并起来
#             result_dict = {}#多个dict合并后的结果
    if len(temp_list)>1:#大于1说明该项下有值，否则此项未填信息
        if len(temp_list)%2!=0:#奇数项的话人工给他添加上一项
            temp_list.append('未填')
        for i in range(len(temp_list)):
            if i%2==0:
                result[temp_list[i].replace(" ", "").replace("：", '')] = temp_list[i+1]
        return result
    #其他则返回str
    else:
        result_str =  str1
        return result_str
def sub_str(str1):
    '''
    学历：大专;身高：176cm;购车：--;月薪：2000～5000元;住房：--;体重：--;星座：天秤座;民族：--;属相：狗;血型：--;
    去掉str中最后一位的';'
    '''
    if str1[0]==';' and str1[-1]==';':#前后都有;
        return str1[1:-1]
    if str1[-1]==';':#取最后一个字条
        return str1[0:-1]#去掉了最后一位
    if str1[0]==';':#取第一个字条
        return str1[1:]#去掉了第一位
    else:
        return str1
    
    
def read_redis_list():#list
    start=0
    end=299
    total_num = r.llen('jiayuan_item:items')#总的item数量
    print("jiayuan_item:items当前数量",total_num)
    while total_num>0:
        data=[]
        sql_data_result=[]
        item_dict={}
        with r.pipeline(transaction=False) as p:
            p.lrange('jiayuan_item:items',start,end)#每取50条执行一次
            data = p.execute()[0]
            print("jiayuan_item:items当前数量",total_num)
            for  item in data:
                sql_data={}
                temp_info = json.loads(item)
                print("当前的item",temp_info)
#                 print("a",type(temp_info),temp_info)
    #             print("person_info",sub_str(a['person_info']))
    #             print("life_style",sub_str(a['life_style']))
    #             print("economic_strength",sub_str(a['economic_strength']))
    #             print("marriage_concep",sub_str(a['marriage_concep']))
    #             print("work_study",sub_str(a['work_study']))
    #             print("find_mate",a['find_mate'])
    #             print("find_mate",sub_str(a['find_mate']))
#                 print("housework",temp_info['housework'])
#                 print("pet",temp_info['pet'])
    
    #             print("person_info",len(sub_str(a['person_info']).split(';')),sub_str(a['person_info']).split(';'))
    #             print("life_style",len(sub_str(a['life_style']).split(';')),sub_str(a['life_style']).split(';'))
    #             print("economic_strength",len(a['economic_strength'].split(';')),a['economic_strength'].split(';'))
    #             print("marriage_concep",len(a['marriage_concep'].split(';')),a['marriage_concep'].split(';'))
#                 print("work_study",len(temp_info['work_study'].split(';')),temp_info['work_study'].split(';'))
    #             print("find_mate",len(sub_str(a['find_mate']).split(';')),sub_str(a['find_mate']).split(';'))
                #person_info一直有值
    #             person_dict = parse(a['person_info'])
    #             print("person_dict",type(person_dict),person_dict)
                '''
                先处理最后一位是';'的，去掉分号以方便split成列表
                person_info后面有;
                life_style后面没有;
                economic_strength没有;
                marriage_concep没有;
                work_study没有;
                find_mate第一个字符为;
                '''
                
                sql_data['age_info']=temp_info['age_info']
                sql_data['sex']=temp_info['sex']
                sql_data['img_urls']=','.join(temp_info['img_urls'])
                sql_data['age']=temp_info['age']
                sql_data['municipal']=temp_info['municipal']
                sql_data['address']=temp_info['address']
                sql_data['person_id']=temp_info['person_id']
                sql_data['url']=temp_info['url']
                sql_data['nike_name']=temp_info['nike_name']
                sql_data['province']=temp_info['province']
                sql_data['image_dir']=temp_info['image_dir']+'_'+len(temp_info['img_urls'])
                sql_data['introduce_oneself']=temp_info['introduce_oneself']
                
                sql_data['interest_label']=temp_info['interest_label']#爱好
                sql_data['personality_label']=temp_info['personality_label']#个人标签
                sql_data['img_num']=len(temp_info['img_urls'])
                
                
                '''
                处理宠物，家务标签
                housework与pet传过来的都是list
                '''
                print("temp_info['housework']",temp_info['housework'])
                print("temp_info['pet']",temp_info['pet'])
                if len(temp_info['housework'])==2:#说明正常
                    sql_data['housework'] = temp_info['housework'][0]
                    sql_data['pet'] = temp_info['housework'][1]
                elif len(temp_info['housework'])==1:
                    if '不会' in temp_info['housework'] or '会一些' in temp_info['housework'] or '精通' in temp_info['housework']:
                        sql_data['housework'] = temp_info['housework'][0]
                        sql_data['pet'] = '未填'
                    else:
                        sql_data['housework']='未填'
                        sql_data['pet'] = temp_info['housework'][0]
                else:
                    sql_data['housework'] = '未填'
                    sql_data['pet'] = '未填'
                    
                if len(temp_info['pet'])==2:#说明正常
                    sql_data['household_assignment'] = temp_info['pet'][0]
                    sql_data['about_pets'] = temp_info['pet'][1]
                elif len(temp_info['pet'])==1:
                    if '不喜欢' in temp_info['pet'] or '还可以' in temp_info['pet'] or  '很喜欢' in temp_info['pet']:
                        sql_data['pet'] = temp_info['pet'][0]
                        sql_data['household_assignment'] = '未填'
                    else:
                        sql_data['pet'] = '未填'
                        sql_data['household_assignment'] = temp_info['pet'][0]
                else:
                    sql_data['pet'] = '未填'
                    sql_data['household_assignment'] = '未填'
                print("sql_data['housework']",sql_data['housework'])
                print("sql_data['household_assignment']",sql_data['household_assignment'])
                print("sql_data['pet']",sql_data['pet'])
                print("sql_data['about_pets']",sql_data['about_pets'])
                
                
                
                '''
                处理person_info一定有值
                '''
                person_info = parse1(sub_str(temp_info['person_info']).split(';'))
                sql_data['education']=person_info['学历']
                sql_data['height']=person_info['身高']
                sql_data['buy_car']=person_info['购车']
                sql_data['salary']=person_info['月薪']
                sql_data['housing']=person_info['住房']
                sql_data['weight']=person_info['体重']
                sql_data['constellation']=person_info['星座']
                sql_data['nation']=person_info['民族']
                sql_data['zodiac']=person_info['属相']
                sql_data['blood_type']=person_info['血型']
                '''
                处理择偶要求find_mate一定有值
                '''
                find_mate = parse2(';'.join(sub_str(temp_info['find_mate']).split('：')).replace(';;',';'))
                sql_data['age_mate'] = find_mate['年龄']
                sql_data['height_mate'] = find_mate['身高']
                sql_data['nation_mate'] = find_mate['民族']
                sql_data['education_mate'] = find_mate['学历']
                sql_data['image_mate'] = find_mate['相册']
                sql_data['marital_status'] = find_mate['婚姻状况']
                sql_data['address_mate'] = find_mate['居住地']
                sql_data['sincerity_mate'] = find_mate['诚信']#诚信
                
                '''
               处理 生活方式不一定有
                '''
                if(len(sub_str(temp_info['life_style']).split(';'))<=2):#说明该项目未填写
                    sql_data['smoke'] = '你很想了解她的生活方式吧，邀请她补充'
                    sql_data['drink_wine'] = '你很想了解她的生活方式吧，邀请她补充'
                    sql_data['exercise_habits'] = '你很想了解她的生活方式吧，邀请她补充'
                    sql_data['eating_habits'] = '你很想了解她的生活方式吧，邀请她补充'
                    sql_data['shopping'] = '你很想了解她的生活方式吧，邀请她补充'
                    sql_data['religious_belief'] = '你很想了解她的生活方式吧，邀请她补充'
                    sql_data['time_table'] = '你很想了解她的生活方式吧，邀请她补充'
                    sql_data['circle_of_communication'] = '你很想了解她的生活方式吧，邀请她补充'
                    sql_data['maximum_consumption'] = '你很想了解她的生活方式吧，邀请她补充'
                else:#说明有值
                    life_style = parse2(sub_str(temp_info['life_style'].replace(';;',';')))
                    sql_data['smoke'] = life_style['吸烟']
                    sql_data['drink_wine'] = life_style['饮酒']
                    sql_data['exercise_habits'] = life_style['锻炼习惯']
                    sql_data['eating_habits'] = life_style['饮食习惯']
                    sql_data['shopping'] = life_style['逛街购物']
                    sql_data['religious_belief'] = life_style['宗教信仰']
                    sql_data['time_table'] = life_style['作息时间']
                    sql_data['circle_of_communication'] = life_style['交际圈子']
                    sql_data['maximum_consumption'] = life_style['最大消费']
                '''
                处理 经济实力一定有
                '''
                if(len(sub_str(temp_info['life_style']).split(';'))<=2):#说明该项目未填写
                    sql_data['salary_economic'] = '你很想了解她的 经济实力吧，邀请她补充'
                    sql_data['buy_house_economic'] = '你很想了解她的经济实力吧，邀请她补充'
                    sql_data['buy_car_economic'] = '你很想了解她的经济实力吧，邀请她补充'
                    sql_data['economic_concept'] = '你很想了解她的经济实力吧，邀请她补充'
                    sql_data['investment_financing'] = '你很想了解她的经济实力吧，邀请她补充'
                    sql_data['foreign_debt'] = '你很想了解她的经济实力吧，邀请她补充'
                   
                else:#说明有值
                    economic_strength = parse2(sub_str(temp_info['economic_strength'].replace(';;',';')))
                    sql_data['salary_economic'] =  economic_strength['月薪']
                    sql_data['buy_house_economic'] =  economic_strength['购房']
                    sql_data['buy_car_economic'] =  economic_strength['购车']
                    sql_data['economic_concept'] =  economic_strength['经济观念']
                    sql_data['investment_financing'] =  economic_strength['投资理财']
                    sql_data['foreign_debt'] =  economic_strength['外债贷款']
                '''
                处理工作学习
                '''
                if(len(sub_str(temp_info['work_study']).split(';'))<=5):#说明该项目未填写
                    sql_data['position'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['company'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['company_type'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['welfare'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['working'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['transfer_work'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['work_family'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['overseas_job'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['university'] =  '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['major'] =  '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['language'] = '你很想了解她的工作学习吧，邀请她补充'
                else:#说明有值
                    work_study = parse2(sub_str(temp_info['work_study'].replace(';;',';')))
                    print("work_study_else",work_study)
                    if '职业职位' in work_study:
                        sql_data['position'] =  work_study['职业职位']
                    else:
                        sql_data['university'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '公司行业' in work_study:
                        sql_data['company'] =  work_study['公司行业']
                    else:
                        sql_data['university'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '公司类型' in work_study:
                        sql_data['company_type'] =  work_study['公司类型']
                    else:
                        sql_data['university'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '福利待遇' in work_study:
                        sql_data['welfare'] =  work_study['福利待遇']
                    else:
                        sql_data['university'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '工作状态' in work_study:
                        sql_data['working'] =  work_study['工作状态']
                    else:
                        sql_data['university'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '调动工作可能性' in work_study:
                        sql_data['transfer_work'] =  work_study['调动工作可能性']
                    else:
                        sql_data['university'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '事业与家庭' in work_study:
                        sql_data['work_family'] =  work_study['事业与家庭']
                    else:
                        sql_data['university'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '海外工作可能性' in work_study:
                        sql_data['overseas_job'] =  work_study['海外工作可能性']
                    else:
                        sql_data['university'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '毕业院校' in work_study:
                        sql_data['university'] =  work_study['毕业院校']
                    else:
                        sql_data['university'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '专业类型' in work_study:
                        sql_data['major'] =  work_study['专业类型']
                    else:
                        sql_data['major'] =  '你很想了解她的学习情况吧，邀请她补充'
                    if '语言能力' in work_study:
                        sql_data['language'] =  work_study['语言能力']
                    else:
                        sql_data['language'] =  '你很想了解她的学习情况吧，邀请她补充'
                '''
                处理婚姻观念
                '''
                if(len(sub_str(temp_info['marriage_concep']).split(';'))<=25):#说明该项目未填写
                    sql_data['position'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['company'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['company_type'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['welfare'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['working'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['transfer_work'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['work_family'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['overseas_job'] = '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['university'] =  '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['major'] =  '你很想了解她的工作学习吧，邀请她补充'
                    sql_data['language'] = '你很想了解她的工作学习吧，邀请她补充'
                else:#说明有值
                    marriage_family = parse2(sub_str(temp_info['marriage_concep'].replace(';;',';')))
                    print("marriage_concep_tmp",marriage_family)
                    sql_data['address_marriage'] =  marriage_family['籍贯']
                    sql_data['registered_residence'] =  marriage_family['户口']
                    sql_data['nationality'] =  marriage_family['国籍']
                    sql_data['personality'] =  marriage_family['个性待征']
                    sql_data['humor'] =  marriage_family['幽默感']
                    sql_data['temper'] =  marriage_family['脾气']
                    sql_data['feelings'] =  marriage_family['对待感情']
                    sql_data['want_child'] =  marriage_family['是否要小孩']
                    sql_data['when_mary'] =  marriage_family['何时结婚']
                    sql_data['strange_love'] =  marriage_family['是否能接受异地恋']
                    sql_data['ideal_marriage'] =  marriage_family['理想婚姻']
                    
                    if '愿与对方父母同住' in marriage_family:
                        sql_data['live_parents'] =  marriage_family['愿与对方父母同住']
                    else:
                        sql_data['live_parents'] =  '你很想了解她的婚姻观念，邀请她补充'
                    if '家中排行' in marriage_family:
                        sql_data['rankings_home'] =  marriage_family['家中排行']
                    else:
                        sql_data['rankings_home'] =   '你很想了解她的婚姻观念，邀请她补充'
                    if '父母情况' in marriage_family:
                        sql_data['parents_situation'] =  marriage_family['父母情况']
                    else:
                        sql_data['parents_situation'] =   '你很想了解她的婚姻观念，邀请她补充'
                    if '兄弟姐妹' in marriage_family:
                        sql_data['brothers'] =  marriage_family['兄弟姐妹']
                    else:
                        sql_data['brothers'] =   '你很想了解她的婚姻观念，邀请她补充'
                    if '父母经济情况' in marriage_family:
                        sql_data['parents_economic'] =  marriage_family['父母经济情况']
                    else:
                        sql_data['parents_economic'] =   '你很想了解她的婚姻观念，邀请她补充'
                    if '父母医保情况' in marriage_family:
                        sql_data['parents_medical'] =  marriage_family['父母医保情况']
                    else:
                        sql_data['parents_medical'] =   '你很想了解她的婚姻观念，邀请她补充'
                    if '父母的工作' in marriage_family:
                        sql_data['parents_working'] =  marriage_family['父母的工作']
                    else:
                        sql_data['parents_working'] =   '你很想了解她的婚姻观念，邀请她补充'
                    sql_data_result.append(sql_data)
                #下载图片
                download_imgs(temp_info['image_dir'],temp_info['sex'],temp_info['img_urls'])
            sql_excute(sql_data_result)#
    #                 print("jiayuan_item:items",type(url),url)
        #从redis写入数据库
            total_num -=299
            start +=299
            end +=299
#         print("sql_data_result",type(sql_data_result),len(sql_data_result),sql_data_result)
def download_imgs(name_persionid,sex,img_list):
    if sex=='男':#选择性别下载图片
        return None
    else:
        '''
        为了防止封IP，下载图片这里也使用代理IP
        '''
    #     conn = connect()
    #     cursor=conn.cursor()
    #     cursor.execute('select ip_port,user_agent from proxy_ip')
    #     datas = cursor.fetchall()
    #     print("datas",datas)
    #     header_ip = datas[random.randint(0,len(datas))]
        header={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"}
        ip={}
    #     f_ip = "D:\\Program Files\\Python_Workspace\\spiders\\p_scrapy\\test_spiders\\test_spiders\\proxy_ip.txt"
    #     f_ip="E:\\soft\\python3.4\\workspace\\spiders\\p_scrapy\\jiayuan\\jiayuan\\proxy_ip.txt"
    #     with open (f_ip,'r') as f:
    #         for line in f.readlines():
    #             print("line",line)
    #             ip['http']=line
        ip['https']='111.8.191.150:8908'#有些代理IP是http,有些是https
        imgPath=IMAGES_STORE  # 下载图片的保存路径在settin中设置
        img_dir = os.path.join(imgPath,parse_filename(name_persionid))
        bad_images=[]#下载失败的图片
        print("图片存放路径 ",img_dir)
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        for i in range(len(img_list)):#name_persionid[name_persionid.find('_')+1:name_persionid.rfind('_')]是取年龄的
            #[parse_filename(name_persionid).find('_')+1:parse_filename(name_persionid).rfind('_')]
            filename = os.path.join(img_dir,name_persionid+'_'+str(i)+'.jpg')
            if os.path.exists(filename):#如果存在的话就跳过
                continue
            try:
                print("当前下载的图片",img_list[i])
                response = requests.get(img_list[i],proxies=ip, headers=header)
    #             img = response.content
                with open(filename, 'wb') as handle:
                    response = requests.get(img_list[i], stream=True)
                    for block in response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)
            except Exception as e:
                print("图片下载失败:%s--->%s" %(img_list[i],str(e)))
                bad_images.append(img_list[i])
        r.sadd('bad_jiayuan_images',bad_images)#将下载失败的图片添加到集合中

def parse_filename(file_name):
    """
    :param path: 需要清洗的文件夹名字
    :return: 清洗掉Windows系统非法文件夹名字的字符串
    """
    file_name = urllib.parse.unquote(file_name)#先将里面的16进制转换一下
    rstr = r"[\/\\\:\*\?\"\<\>\\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", file_name)  # 替换为下划线
    return new_title
    #喂,要幸福\x0e_33岁_32595588'

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

def sql_excute(sql_data):
    '''
    为了保证速度，全部使用insert方式，不考虑重复，因为在scrapy_redis中已去除了重复的url了，理论上
    是没有重复数据的
    传入的是list，所以需要先将其中的item（是str类型的转成dict）使用json.loads转dict
    '''
    conn=connect()
    cursor=conn.cursor()
    print("sql_data",sql_data)
    
    
#     sql_all_info = "insert into all_info (person_id,nike_name,age,sex,address,province,municipal,age_info,\
#                     image_dir,url,person_info,introduce_oneself,find_mate,economic_strength,work_study,\
#                     life_style,marriage_concep,img_urls,img_num) \
#                     values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    
    sql_insert_economic_strength = "insert into economic_strength (person_id,salary,buy_house,buy_car,economic_concept,investment_financing,foreign_debt) \
                    values(%s,%s,%s,%s,%s,%s,%s)"
    
    sql_insert_life_style = "insert into life_style(person_id,smoke,drink_wine,exercise_habits,eating_habits,shopping,religious_belief,time_table,circle_of_communication,maximum_consumption,housework,household_assignment,pet,about_pets) \
                             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
     
    sql_insert_marriage_concep = "insert into marriage_concep(person_id,address,registered_residence,nationality,personality,humor,temper,feelings,want_child,when_mary,strange_love,ideal_marriage,live_parents,rankings_home,parents_situation,brothers,parents_economic,parents_medical,parents_working) \
                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                     
    sql_insert_mate_selection = "insert into mate_selection(person_id,age,height,nation,education,image,marital_status,address,sincerity) \
                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    sql_insert_person_info = "insert into person_info(nike_name,person_id,province,sex,age,municipal,age_info,education,height,buy_car,address,salary,housing,constellation,nation,weight,zodiac,blood_type,introduce_oneself,personality_label,interest_label,img_urls,url,image_dir,img_num) \
                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    sql_insert_work_study = "insert into work_study(person_id,position,company,company_type,welfare,working,transfer_work,work_family,overseas_job,university,major,language) \
                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    
    if isinstance (sql_data,list):
        for item in sql_data:
            try:
                #经济实力表
                print("执行economic_strength")
                cursor.execute(sql_insert_economic_strength, (item['person_id'],item['salary_economic'],item['buy_house_economic'],item['buy_car_economic'],\
                           item['economic_concept'],item['investment_financing'],item['foreign_debt']))
            except Exception as e:
                print("执行错误sql_insert_economic_strength",str(e))
#                 conn.rollback()
                #生活方式表
            try:
                print("执行life_style")
                cursor.execute(sql_insert_life_style,(item['person_id'],item['smoke'],item['drink_wine'],item['exercise_habits'],\
                           item['eating_habits'],item['shopping'],item['religious_belief'],item['time_table'],item['circle_of_communication'],item['maximum_consumption'],item['housework'],\
                           item['household_assignment'],item['pet'],item['about_pets']))
            except Exception as e:
                print("执行错误sql_insert_life_style",str(e))
#                 conn.rollback()   
                #婚姻态度表
            try:
                print("执行marriage_concep")
                cursor.execute(sql_insert_marriage_concep,(item['person_id'],item['address_marriage'],item['registered_residence'],item['nationality'],\
                           item['personality'],item['humor'],item['temper'],item['feelings'],item['want_child'],item['when_mary'],item['strange_love'],\
                           item['ideal_marriage'],item['live_parents'],item['rankings_home'],item['parents_situation'],item['brothers'],item['parents_economic'],item['parents_medical'],item['parents_working']))
            except Exception as e:
                print("执行错误sql_insert_marriage_concep",str(e))
#                 conn.rollback()
                
            try:
                #择偶标准表
                print("执行mate_selection")
                cursor.execute(sql_insert_mate_selection,(item['person_id'],item['age_mate'],item['height_mate'],item['nation_mate'],\
                           item['education_mate'],item['image_mate'],item['marital_status'],item['address_mate'],item['sincerity_mate']))
            except Exception as e:
                print("执行错误sql_insert_mate_selection",str(e))
#                 conn.rollback()
            try:
                #个人信息表
                print("执行person_info")
                cursor.execute(sql_insert_person_info,(item['nike_name'],item['person_id'],item['province'],item['sex'],item['age'],item['municipal'],item['age_info'],item['education'],item['height'],item['buy_car'] \
                                                   ,item['address'],item['salary'],item['housing'],item['constellation'],item['nation'],item['weight'],item['zodiac'],item['blood_type'],item['introduce_oneself'] \
                                                  ,item['personality_label'],item['interest_label'],item['img_urls'],item['url'],item['image_dir'],item['img_num']))
            except Exception as e:
                print("执行错误sql_insert_person_info",str(e))
#                 conn.rollback()  
            try:   
                #工作学习表
                cursor.execute(sql_insert_work_study,(item['person_id'],item['position'],item['company'],item['company_type'],item['welfare'],item['working'],item['transfer_work'],item['work_family'] \
                                                  ,item['overseas_job'],item['university'],item['major'],item['language']))
            except Exception as e:
                print("执行错误sql_insert_work_study",str(e))
#                 conn.rollback()
            finally:
                conn.commit()
    else:
        print("sqldata小于或等于1个")
    

def read_redis_set():
    print("当前set中有数据",r.scard("person_url"))
#     print("所有数据",type(r.smembers("person_url")),r.smembers("person_url"))
    a = list(r.smembers("person_url"))
    print("aa",type(a),len(a),a)
    
if __name__=="__main__":
    total_num = r.llen('jiayuan_last:items')
    print("total_num",total_num)
#     read_redis_list()
#     a='学历：大专;身高：176cm;购车：--;月薪：2000～5000元;住房：--;体重：--;星座：天秤座;民族：--;属相：狗;血型：--;'
    a=';年龄：26-29岁之间;身高：169-185厘米;民族：汉族;学历：不限;相册：有照片;婚姻状况：未婚居住地：;湖北十堰诚信：不限'
    c = ['学历：本科', '身高：160cm', '购车：暂未购车', '月薪：2000～5000元', '住房：与父母同住', '体重：55公斤', '星座：天蝎座', '民族：汉族', '属相：羊', '血型：AB型']
    b = sub_str(a)
#     print(b)
#     d = parse(c)[0]
#     print(d)
#     print(d['身高'])
#     name = '假装狠幸福_女_31岁_100000214'
# #     download_imgs()
#     r.sadd('b',['a','b',3])
    
    '''
    下载图片
    '''
#     start=0
#     end=299
#     total_num = r.llen('jiayuan_item:items')#总的item数量
#     print("jiayuan_item:items当前数量",total_num)
#     while total_num>0:
#         data=[]
#         sql_data_result=[]
#         item_dict={}
#         with r.pipeline(transaction=False) as p:
#             p.lrange('jiayuan_item:items',start,end)#每取50条执行一次
#             data = p.execute()[0]
#             print("jiayuan_item:items当前数量",total_num)
#             for  item in data:
#                 temp_info = json.loads(item)
#                 print("temp_info",temp_info)
#                 download_imgs(temp_info['image_dir'],temp_info['sex'],temp_info['img_urls'])

#     a='不会'
#     b='会一些'
#     c='精通'
#     l=['不会','会一些','精通']
#     if a in l:
#         print(a)
#     else:
#         print("不在里面")

