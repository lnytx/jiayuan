# jiayuan

反复实验了很多的想法，
1、直接通过search接口
  http://search.jiayuan.com/v2/search_v2.php拼接url
  "http://search.jiayuan.com/v2/index.php?key=&sex=f&stc=&sn=default&sv=1&p=%s&pt=%s&ft=off&f=select&mt=d" %(p,info['pageTotal'])
  p是页面number
  pageTotal是当前查询的总页数
  Spider不断yield(twisted异步)这些url(request)到 Scrapy引擎之后返回Response
  在2000条记录时发现有非常大量的重复，之后重复比继续增大，排除这种方式
2、通过数据接口
先构造post参数
data = {
    'sex': 'f',
    'key':'',
    'stc':'', 
    'sn': 'default',
    'sv': 2,
    'p': str(i),
    'f': 'select',
    'listStyle': 'bigPhoto',
    'pri_uid':'',
    'jsversion': 'v5',
}
然后通过scrapy.FormRequest.from_response提交，想获取结果数据，发现改变p结果跟第一中方式一样，都是重复数据，不明白为什么网上有人使用这种方式能获取数据
大概的看了一个，发现这种方式有一长串的hash值，无法破解，这种方式不行
3、通过webdriver先进入搜索页面的第一页
  http://search.jiayuan.com/v2/index.php?key=&sex=f&stc=&sn=default&sv=1&p=699&pt=163649&ft=off&f=select&mt=d
  然后在中间件通过
  next_page = driver.find_element_by_link_text("下一页")
  next_page.click()
  去一页一页的点击，想通过这种方式获取页面人员详细url
  结果发现2500条记录之后详情url就会一直出现重复，这种方式也不可取
4、最后直接使用最保险，获取的数据最多（无需通过搜索页面）直接构造url，当2开头的数据出现后，应该可以结束掉了，佳缘应该是没有那么多会员的
  for p in range(100000000,999999999):
      url = "http://www.jiayuan.com/%s" %(p)
      yield Request(url=url,callback=self.get_main_info)
   先构造9位数的url，在第一个项目create_jiayuan_urls中验证并将有效的与无效的都记录在redis中（可以是一台中心redis，
   多个slave端同时写，因为由于scrapy-redis自带的去重机制BloomFilter来说，不可能两个slave同时写一条url）
   然后再起一个项目jiayuan_details，从redis中读取这些url(高并发的读由redis自己来控制)，获取item(此处要求item尽可能的少，然后尽可能的少一些
   逻辑控制，否则下载中间件会出现瓶颈)
   通过create_jiayuan_urls获取详情url(可以分布式操作)
   通过jiayuan_details获取最后的详细信息(可以分布式操作)理论上只要代理IP给力，这个架构还是很不错的
   get_proxy_ip.py获取几个网站的proxy_ip验证并写入数据库
   from_redis_to_mysql.py这里的方法是根据redis中存储的item下载图片，并将item格式化之后存储到mysql中
   无图无真相


人员基本信息表
![ABC](https://github.com/lnytx/jiayuan/blob/master/images/%E4%BA%BA%E5%91%98%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF.png) 


代理IP表
![ABC](https://github.com/lnytx/jiayuan/blob/master/images/%E4%BB%A3%E7%90%86IP%E8%A1%A8.png)

婚姻观念表
![git1](https://github.com/lnytx/jiayuan/blob/master/images/%E5%A9%9A%E5%A7%BB%E8%A7%82%E5%BF%B5%E8%A1%A8.png)

工作学习表
![git2](https://github.com/lnytx/jiayuan/blob/master/images/%E5%B7%A5%E4%BD%9C%E5%AD%A6%E4%B9%A0%E8%A1%A8.png)

择偶标准表
![git3](https://github.com/lnytx/jiayuan/blob/master/images/%E6%8B%A9%E5%81%B6%E6%A0%87%E5%87%86%E8%A1%A8.png)

生活方式表
![salt-cmd1](https://github.com/lnytx/jiayuan/blob/master/images/%E7%94%9F%E6%B4%BB%E6%96%B9%E6%B3%95.png)

经济实力表
![ABC](https://github.com/lnytx/jiayuan/blob/master/images/%E7%BB%8F%E6%B5%8E%E5%AE%9E%E5%8A%9B%E8%A1%A8.png)


redis中的item
![ABC](https://github.com/lnytx/jiayuan/blob/master/images/items.png)

docker运行
![ABC](https://github.com/lnytx/jiayuan/blob/master/images/docker_redis.png)

下载的人员图片
![ABC](https://github.com/lnytx/jiayuan/blob/master/images/%E4%BA%BA%E5%91%98%E5%9B%BE%E7%89%87.png)

