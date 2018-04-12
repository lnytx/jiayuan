# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JiayuanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    
        #person_info表
    person_info = scrapy.Field()#包括所有的人员信息
    
    nike_name = scrapy.Field()#昵称
    person_id = scrapy.Field()
    province = scrapy.Field()#省
    municipal = scrapy.Field()#市
    image_dir = scrapy.Field()
    age = scrapy.Field()
    sex = scrapy.Field()
    age_info = scrapy.Field()#年龄地址信息
    address = scrapy.Field()
    introduce_oneself = scrapy.Field()#自我介绍
    img_urls = scrapy.Field()#相片url保存地址
    url = scrapy.Field()#人个主页url
    
    interest_label = scrapy.Field()#兴趣爱好
    personality_label = scrapy.Field()#个人标签
    
    #mate_selection择偶标准表
    find_mate = scrapy.Field()#包括所有的择偶信息，没有细分字段
    
    #life_style生活方式表
    life_style = scrapy.Field()
    housework = scrapy.Field()#家务
    pet = scrapy.Field()
    
    
    #economic_strength经济实力表
    economic_strength = scrapy.Field()
    
    
    #work_study工作与学习表
    work_study = scrapy.Field()
    
    
    
    #marriage_concep婚姻观念表
    marriage_concep = scrapy.Field()
    
    
