#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : zl_count.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/3/31 下午4:55
@Desc  : 
"""
import sys
sys.path.append('/root/other_bid_project/Muto') # 你的项目路径
import hashlib
import random
import time

import requests
import hashlib
import json
import datetime
import random
import time

import requests
from app.moen_app import moenApp
from model.rds import rds_206_11


def get_zl_data(date):

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://www.zhiliaobiaoxun.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.zhiliaobiaoxun.com/search/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    params = {
        'page': '2',
        'count': '10',
        'date': date + '_' + date,
    }
    params = deal_params(params)
    response = requests.get('https://api-service-zhiliao.bailian-ai.com/search/bid', params=params, headers=headers)
    data = response.json()
    total = data['data']['total']
    return total


def deal_params(params):
    keyword = params.get('keyword', '')
    random_num = random.randint(200, 400)
    # print(random_num)
    timestamp = str(int(time.time()*1000-random_num))
    # print(timestamp)
    hash_ = sign(keyword + timestamp + 'zlbxdc406fce62db4066b1f586677c9')
    # print(hash_)
    params['timestamp'] = timestamp
    params['hash'] = hash_
    return params

def sign(data):
    str_md5 = hashlib.md5(data.encode(encoding='utf-8')).hexdigest()
    return str_md5



if __name__ == '__main__':
    today = datetime.datetime.today()
    yesterday = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    count = get_zl_data(yesterday)
    rds_206_11.hset('jianyu:zl_title:count', yesterday, count)
    print(datetime.datetime.now(), yesterday, count)
