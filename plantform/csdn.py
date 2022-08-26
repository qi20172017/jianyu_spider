#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : csdn_spider.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2022/2/9 下午5:31
@Desc  :
"""
import time
from lxml import etree
import json
import requests

from app.moen_app import moenApp
from model.msql.my_dao.my_csdn_dao import MyCsdnDao


@moenApp.task(
    name='moen.csdn.article',
    bind=True,
    acks_late=True,
    rate_limit='10/m',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def get_data(self, author, page):
    url = f"https://blog.csdn.net/community/home-api/v1/get-business-list?page={page}&size=20&businessType=blog&orderby=&noMore=false&year=&month=&username={author}"
    payload = {}
    headers = {
        'authority': 'blog.csdn.net',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        'accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://blog.csdn.net/kdl_csdn?type=blog',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    j_data = json.loads(response.text)
    if j_data['message'] == "success":
        data_list = j_data['data']['list']

        if len(data_list) > 0:
            next_page = page + 1
            moenApp.send_task("moen.csdn.article", args=(author, next_page))

        for item in data_list:
            print(item)
            result_data = {}
            result_data['article_id'] = item["articleId"]
            result_data['title'] = item["title"]
            result_data['description'] = item["description"]
            result_data['url'] = item["url"]
            result_data['article_type'] = item["type"]
            result_data['top'] = item["top"]
            result_data['author'] = author

            result_data['view_count'] = item["viewCount"]
            result_data['comment_count'] = item["commentCount"]
            result_data['like_count'] = item["diggCount"]

            result_data['item_id'] = str(result_data['article_id']) + '@' + str(int(time.time()*1000))

            result_data['create_time'] = item["postTime"]

            result_data['platform'] = 'csdn'
            MyCsdnDao.upsert(**result_data)



if __name__ == '__main__':
    # page_data = get_data('weixin_43471909', 1)
    page_data = get_data('kdl_csdn', 3)
    # clean_data(page_data)
    # print(int(time.time()*1000))

    # aa = []
    # print(len(aa))
    # result = MyCsdnDao.get('18987865@1644473472241')
    # print(result)
