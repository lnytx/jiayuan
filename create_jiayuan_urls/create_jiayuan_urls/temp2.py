# -*- coding:utf-8 -*-
'''
测试用，可删除
'''

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



login_url = 'http://login.jiayuan.com/'#登录时的url
option = webdriver.ChromeOptions()
prefs={"profile.managed_default_content_settings.images":2}#禁止加载图片
option.add_experimental_option("prefs",prefs)
option.add_argument('--headless')
option.add_argument("--window-size=1920,1080")
# option.add_argument(pro_ip['user_agent'])#自定ageng
# option.add_argument('--proxy-server=http://'+pro_ip['ip_port'])
# option.add_argument("--proxy-server=http://222.73.68.144:8090")
pool=redis.ConnectionPool(host='127.0.0.1',port=6379,db=0,decode_responses=True)  #427条记录
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
        driver.save_screenshot('login.png')
except Exception as e:
    driver.close()
    print("spider出现了异常,关闭",str(e))
#         