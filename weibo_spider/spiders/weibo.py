# -*- coding: utf-8 -*-
#参考 https://www.jianshu.com/p/5d1061f09a1f
import json

import scrapy
from scrapy import Request
from bs4 import BeautifulSoup as bs

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['m.weibo.cn']

    def __init__(self,*args,**kwargs):
        super(WeiboSpider, self).__init__(*args, **kwargs)
        # 大V公众号&个人账号
        self.start_urls = ['https://m.weibo.cn/p/1005052803301701',
                           'https://m.weibo.cn/u/2189067512']
        self.maxPage = 5 # 指定抓取的最大页数

    # 针对不同的账户类型做不同的请求URL处理
    def start_requests(self):
        containerid = ''
        for start_url in self.start_urls:
            url_head = 'https://m.weibo.cn/api/container/getIndex?containerid='
            if 'https://m.weibo.cn/p/' in start_url:
                containerid = start_url.replace('https://m.weibo.cn/p/','').replace('100505','107603')
            elif 'https://m.weibo.cn/u/' in start_url:
                containerid = '107603' + start_url.replace('https://m.weibo.cn/u/', '')
            if containerid:
                for pagenum in range(self.maxPage):
                    origin_url = '%s%s%s' % (url_head, containerid,'&page='+str(pagenum))
                    yield Request(origin_url, callback=self.parse)

    def parse(self, response):
        content = json.loads(response.body)
        weibo_info = content.get('data').get('cards')
        for info in weibo_info:
            if info.get('mblog') and info.get('mblog').get('text'):
                title = (info['mblog']['text'])
                soup = bs(title,'html.parser')
                title = soup.text
                url = "https://m.weibo.cn/status/%s" % info["mblog"]["mid"]
                time_str = info.get('mblog').get('created_at')
                picture_urls = ''
                if info.get('mblog').get('page_info'):
                    if info.get('mblog').get('page_info').get('media_info'):
                        picture_urls = info.get('mblog').get('page_info').get('page_pic')['url']
                if not picture_urls:
                    if info.get('mblog').get('pics'):
                        pics = map(lambda x: x.get('url'), info["mblog"]["pics"])
                        picture_urls = ','.join(pics)

                print('======微博内容======')
                print(title)
                print(url)
                print(time_str)
                print(picture_urls)
