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
获取详情信息，spider中item越少，对item所做的逻辑控制越少，下载中间件的速度就会越快
然后将下载的item存储在redis中，
可以定期调用 from_redis_to_mysql.py将数据格式化后写入mysql,将图片下载保存
'''

import json
import time

from scrapy  import log
from scrapy import cmdline
import scrapy
from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy_redis.spiders import RedisSpider
from selenium import webdriver


from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from jiayuan_details.items import JiayuanItem
from jiayuan_details.settings import USER_NAME, PASSWD
import redis
import re

pool=redis.ConnectionPool(host='127.0.0.1',port=6379,db=0,decode_responses=True)  #427条记录
r = redis.StrictRedis(connection_pool=pool)  
redis_pipe = r.pipeline()


class jiayuan_data(RedisSpider):

#     allowed_domains = ["jiayuan.com"]
    name = "jiayuan_item"
    
    redis_key = 'jiayuan_item:start_urls'
#     url_base = 'http://search.jiayuan.com/v2/index.php?key=&sex=f&stc=&sn=default&sv=1&p=%s&pt=163649&ft=off&f=select&mt=d'
#     start_urls = []
    '''
        下载器中间件在下载器和Scrapy引擎之间，每一个request和response都会通过中间件进行处理。
        在中间件中，对request进行处理的函数是process_request(request, spider)
    '''
    
    def start_requests(self):#
#         从redis中读取url
        start=0
        end=99
        total_num = r.llen('jiayuan_sccuss:items')#总的item数量
        print("person_url当前数量",total_num)
        while total_num>0:
            with r.pipeline(transaction=False) as p:
                p.lrange('jiayuan_sccuss:items',start,end)#每取50条执行一次
                urls = p.execute()[0]
                print("source",len(urls))
                print("jiayuan_sccuss:items当前数量",total_num)
                for item in urls:
                    url = json.loads(item)
                    yield Request(url=url['url'],callback=self.get_main_info)
        #从redis写入数据库
            total_num -=100
            start +=99
            end +=99   
#         url = 'http://www.jiayuan.com/175017527'
#         yield Request(url=url,dont_filter = True,callback=self.get_main_info)
            
    def get_main_info(self,response):
        item = JiayuanItem()
        age_info = response.xpath('/html//h6[@class="member_name"]').xpath('string(.)').extract()[0]#str 26岁，未婚，来自湖北十堰显示地图
        address = response.xpath('/html//h6[@class="member_name"]/a').xpath('string(.)').extract()#list['湖北', '十堰', '显示地图']
        str_sheng = address[0]
        str_shi = address[1]
        print("人员地址",address[0]+'sssss'+address[1])
        person_id = response.url[response.url.rfind('/')+1:]#175017527
        
        item['person_id'] =  person_id
        item['province'] = str_sheng
        item['municipal'] = str_shi
        nick_name_p = response.xpath('/html//div[@class="member_info_r yh"]/h4').xpath('string(.)').extract()
        nick_name=nick_name_p[0][0:nick_name_p[0].index("I")]
        print("昵称", nick_name)
        item['nike_name'] = nick_name
        '''
          获取性别  
        '''
        sex = response.xpath('/html//div[@class="subnav_box yh"]//ul[@class="nav_l"]/li[@class="cur"]/a/text()').extract()
#         sex2 = response.xpath('/html//div[@class="subnav_box yh"]//ul[@class="nav_l"]//a/text()').extract()
        if sex[0]=='她的资料':
            item['sex']='女'#0为女
        else:
            item['sex']='男'#1为男
        print("性别",sex)
        
        '''
        人个信息
        '''
        person_info = response.xpath('/html//ul[@class="member_info_list fn-clear"]').xpath('string(.)').extract()[0].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;','')
#         print("个人信息",type(person_info),person_info)
        #a=person_info[0].xpath('string(.)').extract().replace('\n                                ','')
            #a=item.xpath('string(.)').extract()[0].replace('\n                                ','')
        '''
        兴趣爱好，个性标签
        '''
        try:
            personality_label=response.xpath('/html//div[@class="test4"]//div[@class="list_a fn-clear"]').xpath('string(.)').extract()[0].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
            item['personality_label'] = personality_label
        except Exception as e:
            item['personality_label'] = '未填'
#         b=response.xpath('/html/body/div[6]/div[1]/div[3]/div/div[1]/div[1]/ul').xpath('string(.)').extract()
        try:
            interest_label=response.xpath('/html/body/div[6]/div[1]/div[3]/div/div[1]/div[1]/ul').xpath('string(.)').extract()[0].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
            item['interest_label'] = interest_label
        except Exception as e:
            item['interest_label'] = '未填'
        try:
            housework = response.xpath('/html//div[@class="bg_white mt15"]')[2].xpath('div[@class="js_box"]//div[@class="pt25 fn-clear"]//dd[@class="cur"]').xpath('string(.)').extract()
            item['housework'] = housework
        except Exception as e:
            item['housework'] = '未填'
        try:
            pet = response.xpath('/html//div[@class="bg_white mt15"]')[2].xpath('div[@class="js_box"]//div[@class="fl pr"]/em').xpath('string(.)').extract()
            item['pet'] = pet
        except Exception as e:
            item['pet'] = '未填'
        '''
        人员信息一起写，这样快一些，后期可以再整理入库
        '''
        item['person_info']="".join(person_info.split())
#         item['education'] = person_info.xpath('string()').extract()[0].replace('\n                                ','')
#         item['height'] = person_info.xpath('string()').extract()[1].replace('\n                                ','')
#         item['buy_car'] = person_info.xpath('string()').extract()[2].replace('\n                                ','')
#         item['salary'] = person_info.xpath('string()').extract()[3].replace('\n                                ','')
#         item['housing'] = person_info.xpath('string()').extract()[4].replace('\n                                ','')
#         item['weight'] = person_info.xpath('string()').extract()[5].replace('\n                                ','')
#         item['constellation'] = person_info.xpath('string()').extract()[6].replace('\n                                ','')
#         item['nation'] = person_info.xpath('string()').extract()[7].replace('\n                                ','')
#         item['zodiac'] = person_info.xpath('string()').extract()[8].replace('\n                                ','')
#         item['blood_type'] = person_info.xpath('string()').extract()[9].replace('\n                                ','')
#         print("学历",item['education'])
#         print("身高",item['height'])
#         print("购车",item['buy_car'])
#         print("月薪",item['salary'])
#         print("住房",item['housing'])
#         print("体重",item['weight'])
#         print("星座",item['constellation'])
#         print("民族",item['nation'])
#         print("属相",item['zodiac'])
#         print("血型",item['blood_type'])
        item['age'] = age_info[0:age_info.index('，')]
        item['address'] = str_sheng+str_shi
        item['age_info'] = age_info
        item['image_dir'] = nick_name+'_'+item['sex']+'_'+item['age']+'_'+person_id#下载的相片归类
        print("相片地址",item['image_dir'])
        item['url'] = response.url
#         '''
        print("当前返回的url",response.url)
        #个人短语
        introduce_oneself = short=response.xpath('/html//div[@class="main_1000 mt15 fn-clear"]//div[@class="js_text"]/text()').extract()[0].replace('\r','').replace('\n ','').replace(' ','')
        item['introduce_oneself'] = "".join(introduce_oneself.split())
        '''
            择偶要求
        '''
        find_mate = response.xpath('/html//div[@class="bg_white mt15"]')[1].xpath('div[@class="js_box"]/ul[@class="js_list fn-clear"]').xpath('string(.)').extract()[0].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
        find_mate = response.xpath('/html//div[@class="bg_white mt15"]')[1].xpath('div[@class="js_box"]/ul[@class="js_list fn-clear"]').xpath('string(.)').extract()[0].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
        item['find_mate'] = "".join(find_mate.split())
        '''
        生活方式
        '''
        life_style = response.xpath('/html//div[@class="bg_white mt15"]')[2].xpath('div[@class="js_box"]/ul[@class="js_list fn-clear"]').xpath('string(.)').extract()[0].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
        item['life_style'] = "".join(life_style.split())
        '''
        经济实力
        '''
        economic_strength = response.xpath('/html//div[@class="bg_white mt15"]')[3].xpath('div[@class="js_box"]/ul[@class="js_list fn-clear"]').xpath('string(.)').extract()[0].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
        item['economic_strength'] = "".join(economic_strength.split())
        '''
        工作学习
        '''
        work_study = response.xpath('/html//div[@class="bg_white mt15"]')[4].xpath('div[@class="js_box"]/ul[@class="js_list fn-clear"]').xpath('string(.)').extract()
        work_pre = work_study[0].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
        work_last = work_study[1].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
        item['work_study'] = "".join(work_pre.split())+"".join(work_last.split())
        '''
        婚姻观念
        '''
        marriage_concep = response.xpath('/html//div[@class="bg_white mt15"]')[5].xpath('div[@class="js_box"]/ul[@class="js_list fn-clear"]').xpath('string(.)').extract()
        pre = marriage_concep[0].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
        last = marriage_concep[1].replace('\r','').replace('\n',';').replace(' ','').replace(';;;;',';').replace(';;',';')
        item['marriage_concep'] = "".join(pre.split())+"".join(last.split())
        '''
        相片列表
        '''
        list_images = response.xpath('/html//div[@id="bigImg"]//a')
        print("相片列表",type(list_images),list_images)
        images= []
        for i in list_images:
            image = i.xpath('img/@src')
            images.append(image.extract()[0])
            print("相片地址",image.extract()[0])
         
        item['img_urls'] = images#保存相片地址，在person_info表中的text
        yield  item
cmdline.execute("scrapy crawl jiayuan_item".split())