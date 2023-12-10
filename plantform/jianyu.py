#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : jianyu.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/1/16 下午4:46
@Desc  : 
"""

import os
import math
import re
import time
from lxml import etree
import json
import requests
from model.rds import rds_206_11
from app.moen_app import moenApp
# from model.msql.my_dao.my_csdn_dao import MyCsdnDao
import random
import hashlib
from hashlib import md5
import datetime
import base64
import cv2
import hashlib
from io import BytesIO
from ufile import config,filemanager
from sonyflake import SonyFlake
from datetime import timedelta

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common.config import judge_notice_type, single_province

from model.msql.my_dao.my_jy_dao import MyJyDao, MyJyTestDao
from kafka import KafkaProducer
from kafka.errors import KafkaError


test = False



bootstrap_servers=['172.16.63.83:9092', '172.16.113.148:9092', '172.16.135.145:9092']


class Kafka_producer():
    '''''
    生产模块：根据不同的key，区分消息
    '''

    def __init__(self):

        self.kafkatopic = "spider_bid"
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers
                )

    def sendjsondata(self, params):
        try:
            parmas_message = json.dumps(params,ensure_ascii=False)
            # print(parmas_message)
            v = parmas_message.encode('utf-8')
            # print("send msg:(k,v)",k,v)
            self.producer.send(self.kafkatopic, v,
                          # key=k,
                          # partition=int(self.key)
                          ).add_callback(self.on_send_success).add_errback(self.on_send_error)
            self.producer.flush()
        except KafkaError as e:
            print(f'error: {e}')
        # 打印成功发送的信息
        self.producer.close()

    def on_send_success(self, record_metadata):
        print("topic:{} partition:{} offset:{}".format(record_metadata.topic, record_metadata.partition,
                                                       record_metadata.offset))
        # 打印失败的信息

    def on_send_error(self, excp):
        print(excp)

class My_Kafka_producer():
    '''''
    生产模块：根据不同的key，区分消息
    '''

    def __init__(self):

        self.kafkatopic = "bid_test_v1"
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers
                )

    def sendjsondata(self, params):
        try:
            parmas_message = json.dumps(params,ensure_ascii=False)
            # print(parmas_message)
            v = parmas_message.encode('utf-8')
            # print("send msg:(k,v)",k,v)
            self.producer.send(self.kafkatopic, v,
                          # key=k,
                          # partition=int(self.key)
                          ).add_callback(self.on_send_success).add_errback(self.on_send_error)
            self.producer.flush()
        except KafkaError as e:
            print (e)
        # 打印成功发送的信息
        self.producer.close()

    def on_send_success(self, record_metadata):
        print("topic:{} partition:{} offset:{}".format(record_metadata.topic, record_metadata.partition,
                                                       record_metadata.offset))
        # 打印失败的信息

    def on_send_error(self, excp):
        print(excp)



@moenApp.task(
    name='bid.jianyu.zl_search',
    bind=True,
    acks_late=True,
    rate_limit='5/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def zl_search(self, data):

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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    mq_data = json.loads(data)
    params = {}
    params['count'] = 10
    params['keyword'] = ''
    params['page'] = mq_data['page']
    params['adcodes'] = mq_data['adcodes']
    params['orgTypes'] = mq_data['orgTypes']
    params['bidProcesses'] = mq_data['bidProcesses']

    page = mq_data['page']


    proxies = get_proxy_ip('')
    params = deal_params(params)

    try:
        response = requests.get(
            'https://api-service-zhiliao.bailian-ai.com/search/bid',
            params=params,
            headers=headers,
            proxies=proxies
        )
        data = response.json()['data']
        records = data['records']
        total = data['total']

    except Exception as e:
        print("ERROR", e, params)
        # moenApp.send_task('bid.jianyu.zl_search', )
        moenApp.send_task('bid.jianyu.zl_search', args=(json.dumps(mq_data),))
        return

    today_date = datetime.datetime.today().strftime('%Y-%m-%d')

    for item in records:
        # title = item['titleText']
        products = item['products']
        for title in products:
            title = title.replace("<font color='red'>", '').replace('</font>', '')

            print(title)
            # count_zl_title(title, mq_data['date'])

            if rds_206_11.sadd(f'jianyu:zl_title_all:{today_date}', title):
                moenApp.send_task('bid.jianyu.search', args=(json.dumps({
                    'keyword': title,
                    'page': 1,
                    'area':''
                }),), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)

    if int(page) == 1:
        max_page = math.ceil(total/10)

        for i in range(2, min(max_page, 3)): # 4.24 第三页就要登录

            mq_data['page'] = i
            next_data = json.dumps(mq_data)
            print(mq_data)
            moenApp.send_task('bid.jianyu.zl_search', args=(next_data,), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)

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


@moenApp.task(
    name='bid.jianyu.zl_search_keyword',
    bind=True,
    acks_late=True,
    rate_limit='5/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def zl_search_keyword(self, data):

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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    mq_data = json.loads(data)
    params = {}
    params['count'] = 10
    params['page'] = mq_data['page']
    params['keyword'] = mq_data['keyword']
    page = mq_data['page']


    proxies = get_proxy_ip('')
    params = deal_params(params)

    try:
        response = requests.get(
            'https://api-service-zhiliao.bailian-ai.com/search/bid',
            params=params,
            headers=headers,
            proxies=proxies,
            timeout=15
        )
        data = response.json()['data']
        records = data['records']
        total = data['total']

    except Exception as e:
        print("ERROR: ", e)
        moenApp.send_task('bid.jianyu.zl_search_keyword', args=(json.dumps(mq_data),))
        return

    # today = datetime.datetime.today()
    # yesterday = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    today_date = datetime.datetime.today().strftime('%Y-%m-%d')

    next_page = True
    for item in records:
        pubTime = item['pubTime']

        next_page = in_limit(pubTime)

        if not next_page:         # 超出时间范围也不要进行下一步了。要不然，2万个词，每个词多个20个，就是40万个，就特别多
            break
        products = item['products']
        for title in products:
            title = title.replace("<font color='red'>", '').replace('</font>', '')

            print(title, pubTime)

            # count_zl_title(title, pubTime)

            if rds_206_11.sadd(f'jianyu:zl_title_all:{today_date}', title):

                moenApp.send_task('bid.jianyu.search', args=(json.dumps({
                    'keyword': title,
                    'page': 1,
                    'area':''
                }),))


    if next_page and int(page) <2:

        mq_data['page'] = int(page) + 1
        next_data = json.dumps(mq_data)
        print(f'翻页：{next_data}')
        moenApp.send_task('bid.jianyu.zl_search_keyword', args=(next_data,), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
        # zl_search_keyword(next_data)


@moenApp.task(
    name='bid.jianyu.search',
    bind=True,
    acks_late=True,
    rate_limit='6/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def search(self, data):

    data = json.loads(data)
    page = data['page']
    keyword = data['keyword']
    area = data['area']

    # phone, cookies = get_cookies_history()
    # if not phone:
    #     print('没有cookies了')
    #     moenApp.send_task('bid.jianyu.search', args=(json.dumps(data),))
    #     time.sleep(60)
    #     return


    headers = {
        'authority': 'www.jianyu360.cn',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cache-control': 'no-cache',
        'origin': 'https://www.jianyu360.cn',
        'pragma': 'no-cache',
        'referer': 'https://www.jianyu360.cn/jylab/supsearch/index.html?keywords=%E5%A4%A7%E6%95%B0%E6%8D%AE&searchvalue=&selectType=title',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    # data = {
    #     'pageNumber': page,
    #     'pageSize': '100',
    #     'reqType': 'bidSearch',
    #     'searchvalue': keyword,
    #     'area': area,
    #     'subtype': '',
    #     'publishtime': 'lately-7',
    #     'selectType': 'content,file,title',
    #     'minprice': '',
    #     'maxprice': '',
    #     'industry': '',
    #     'tabularflag': 'Y',
    #     'buyerclass': '',
    #     'buyertel': '',
    #     'winnertel': '',
    #     'notkey': '',
    #     'fileExists': '0',
    #     'city': '',
    #     'searchGroup': '1',
    #     'searchMode': '0',  # 20231118 0表示精准搜索
    #     'wordsMode': '0',
    #     'additionalWords': '',
    # }

    data = {
        'pageNumber': page,
        'pageSize': '100',
        'reqType': 'bidSearch',
        'searchvalue': keyword,
        'area': '',
        'subtype': '',
        'publishtime': 'thisyear',
        'selectType': 'content,title',
        'minprice': '',
        'maxprice': '',
        'industry': '',
        'tabularflag': 'Y',
        'buyerclass': '',
        'buyertel': '',
        'winnertel': '',
        'notkey': '',
        'fileExists': '0',
        'city': '',
        'searchGroup': '0',
        'searchMode': '0',
        'wordsMode': '0',
        'additionalWords': '',
    }

    url = 'https://www.jianyu360.cn/front/pcAjaxReq'
    # proxies = get_proxy_ip('')
    try:
        response = requests.post(
            url,
            data=data,
            verify=False,
            headers=headers,
            # cookies=cookies,
            proxies=Ipool.get_proxy_ip_dm(),
            timeout=15,
        )
        # rds_206_11.hincrby('jianyu:cookies_count_history', phone)
        if response.status_code == 702:
            raise ValueError
    except Exception as e:
        print('ERROR: ', e)
        moenApp.send_task('bid.jianyu.search', args=(json.dumps({
            'keyword': keyword,
            'page': page,
            'area':area
        }),))
        return
    # res = re.findall('params: (.*),', response.text)
    # if res:
    #     data = json.loads(res[0])
    #     data_list = data['list']
    #     total = data['totalPage']
    # else:
    #     data_list = json.loads(response.text)['list']

    if "<title>验证码</title>" in response.text:
        moenApp.send_task('bid.jianyu.search', args=(json.dumps({
            'keyword': keyword,
            'page': page,
            'area':area
        }),))
        print(f'出现了验证码:{keyword},{page},{area}')
        return
    # print(response.text)
    try:
        data_list = json.loads(response.text)['list']
    except Exception as e:

        print(f'出现错误请求：{data}')
        print(f'错误页面：{response.content.decode()}')
        self.retry(countdown=10)
        return

    if not data_list:
        return

    print('数据的条数：', len(data_list))



    next_page = True
    for bid in data_list:

        _id = bid['_id']
        bid_area = bid.get('area')
        city = bid.get('city')
        publishtime = bid['publishtime']
        title = bid.get('title')
        subtype = bid.get('subtype')
        site = bid.get('site')

        data = {
            '_id': _id,
            'area': bid_area,
            'city': city,
            'publishtime': publishtime,
            'title': title,
            'subtype': subtype,
            'site': site
        }
        # print(data)
        if int(publishtime) < get_zero_time():
            next_page = False
            print(publishtime, time.strftime("%Y-%m-%d", time.localtime(publishtime)))
            break

        not_inquee = rds_206_11.sadd('jianyu:in_quee', _id)
        rds_206_11.sadd(f'jianyu:in_quee_{datetime.date.today()}', _id)
        if not_inquee:
            pass
        else:
            print(f'已经在队列: {_id}')
            continue

        if not rds_206_11.sismember('jianyu:crawled_id', _id):
            print(f'{_id} 有效数据 {time.strftime("%Y-%m-%d", time.localtime(publishtime))}')
            moenApp.send_task('bid.jianyu.detail', args=(json.dumps(data),))
            # rds_206_11.hincrby('jianyu:source_classify', f'zl_{today_date}')
        else:
            print(f'{_id} 已经爬过了')
            pass
    if next_page and len(data_list) == 100 and int(page) < 5:
        # next(key, int(page)+1)
        moenApp.send_task('bid.jianyu.search', args=(json.dumps({
            'keyword': keyword,
            'page': int(page)+1,
            'area': area
        }),), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
        print('翻页',{
            'keyword': keyword,
            'page': int(page)+1,
            'area': area
        })

def get_cookies_history():
    try:
        for i in range(50):
            phone = rds_206_11.rpop('jianyu:account_spider_history').decode()
            print(phone)

            number = rds_206_11.hget('jianyu:cookies_count_history', phone).decode()
            if int(number) < 1500:
                rds_206_11.lpush('jianyu:account_spider_history', phone)
                cookies = json.loads(rds_206_11.hget('jianyu:cookies', phone).decode())
                print(cookies)
                return phone, cookies
        print('没有cookies了')
    except Exception as e:
        print(e)
        return None, None




@moenApp.task(
    name='bid.jianyu.search_keyword',
    bind=True,
    acks_late=True,
    rate_limit='5/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def search_keyword(self, data):

    data = json.loads(data)
    page = data['page']
    keyword = data['keyword']
    area = data['area']
    headers = {
        'authority': 'www.jianyu360.cn',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cache-control': 'no-cache',
        'origin': 'https://www.jianyu360.cn',
        'pragma': 'no-cache',
        'referer': 'https://www.jianyu360.cn/jylab/supsearch/index.html?keywords=%E5%A4%A7%E6%95%B0%E6%8D%AE&searchvalue=&selectType=title',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    req_data = {
        'pageNumber': page,
        'pageSize': '100',
        'reqType': 'bidSearch',
        'searchvalue': keyword,
        'area': area,
        'subtype': '',
        'publishtime': 'lately-7',
        'selectType': 'content,file,title',
        'minprice': '',
        'maxprice': '',
        'industry': '',
        'tabularflag': 'Y',
        'buyerclass': '',
        'buyertel': '',
        'winnertel': '',
        'notkey': '',
        'fileExists': '0',
        'city': '',
        'searchGroup': '1', #  超前项目看不了详情，1为招标采购公告，不包括超前项目
        'searchMode': '0',
        'wordsMode': '0',
        'additionalWords': '',
    }
    url = 'https://www.jianyu360.cn/front/pcAjaxReq'
    proxies = get_proxy_ip('')
    try:
        response = requests.post(
            url,
            data=req_data,
            verify=False,
            headers=headers,
            proxies=proxies
        )
        if response.status_code == 702:
            raise ValueError
    except Exception as e:
        print('ERROR: ', e)
        moenApp.send_task('bid.jianyu.search_keyword', args=(json.dumps({
            'keyword': keyword,
            'page': page,
            'area':area
        }),))
        return
    # res = re.findall('params: (.*),', response.text)
    # if res:
    #     data = json.loads(res[0])
    #     data_list = data['list']
    #     total = data['totalPage']
    # else:
    #     data_list = json.loads(response.text)['list']

    if "<title>验证码</title>" in response.text:
        moenApp.send_task('bid.jianyu.search_keyword', args=(json.dumps({
            'keyword': keyword,
            'page': page,
            'area':area
        }),))
        print(f'出现了验证码:{keyword},{page},{area}')
        return

    data_list = json.loads(response.text)['list']


    if not data_list:
        return

    print('数据的条数：', len(data_list))

    next_page = True
    for bid in data_list:

        _id = bid['_id']
        bid_area = bid.get('area')
        city = bid.get('city')
        publishtime = bid['publishtime']
        title = bid.get('title')
        subtype = bid.get('subtype')
        site = bid.get('site')

        data = {
            '_id': _id,
            'area': bid_area,
            'city': city,
            'publishtime': publishtime,
            'title': title,
            'subtype': subtype,
            'site': site
        }
        # print(data)

        if publishtime < get_zero_time():
            next_page = False

        not_inquee = rds_206_11.sadd('jianyu:in_quee', _id)
        rds_206_11.sadd(f'jianyu:in_quee_{datetime.date.today()}', _id)

        if not_inquee:
            pass
        else:
            print(f'已经在队列: {_id}')
            continue

        if not rds_206_11.sismember('jianyu:crawled_id', _id):
            print(f'{_id} 有效数据')
            moenApp.send_task('bid.jianyu.detail', args=(json.dumps(data),), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
            # rds_206_11.hincrby('jianyu:source_classify', f'zl_{today_date}')
        else:
            print(f'{_id} 已经爬过了')
            pass
    if next_page and len(data_list) == 100 and int(page) < 5:
        # next(key, int(page)+1)
        moenApp.send_task('bid.jianyu.search_keyword', args=(json.dumps({
            'keyword': keyword,
            'page': int(page)+1,
            'area': area
        }),), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
        print('翻页',{
            'keyword': keyword,
            'page': int(page)+1,
            'area': area
        })

@moenApp.task(
    name='bid.jianyu.require',
    bind=True,
    acks_late=True,
    rate_limit='5/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def search_require(self, data):

    data = json.loads(data)
    page = data['page']
    keyword = data['keyword']
    area = data['area']

    print(f'receive data: {data}')

    headers = {
        'authority': 'www.jianyu360.cn',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cache-control': 'no-cache',
        'origin': 'https://www.jianyu360.cn',
        'pragma': 'no-cache',
        'referer': 'https://www.jianyu360.cn/jylab/supsearch/index.html?keywords=%E5%A4%A7%E6%95%B0%E6%8D%AE&searchvalue=&selectType=title',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    data = {
        'pageNumber': page,
        'pageSize': '100',
        'reqType': 'bidSearch',
        'searchvalue': keyword,
        'area': area,
        'subtype': '',
        'publishtime': 'thisyear',
        'selectType': 'title',
        'minprice': '',
        'maxprice': '',
        'industry': '',
        'tabularflag': 'Y',
        'buyerclass': '',
        'buyertel': '',
        'winnertel': '',
        'notkey': '',
        'fileExists': '0',
        'city': '',
        'searchGroup': '1',
        'searchMode': '0',
        'wordsMode': '0',
        'additionalWords': '',
    }
    url = 'https://www.jianyu360.cn/front/pcAjaxReq'
    proxies = get_proxy_ip('')
    try:
        response = requests.post(
            url,
            data=data,
            verify=False,
            headers=headers,
            proxies=proxies
        )
    except Exception as e:
        print(f'ERROR: {e}')
        moenApp.send_task('bid.jianyu.require', args=(json.dumps({
            'keyword': keyword,
            'page': page,
            'area':area
        }),))
        print(f'请求有问题:{keyword},{page},{area}')
        return

    if response.status_code == 702:
        moenApp.send_task('bid.jianyu.require', args=(json.dumps({
            'keyword': keyword,
            'page': page,
            'area': area
        }),))
        raise ValueError

    if "<title>验证码</title>" in response.text:
        moenApp.send_task('bid.jianyu.require', args=(json.dumps({
            'keyword': keyword,
            'page': page,
            'area':area
        }),))
        print(f'出现了验证码:{keyword},{page},{area}')
        return

    json_data = json.loads(response.text)
    data_list = json_data['list']
    count = json_data['count']
    count_keyword(f'{keyword}_{area}', count)
    if not data_list:
        print(f'page raw data: {response.text}')
        return

    print('数据的条数：', len(data_list))

    next_page = True
    for bid in data_list:

        _id = bid['_id']
        bid_area = bid.get('area')
        city = bid.get('city')
        publishtime = bid['publishtime']
        title = bid.get('title')
        subtype = bid.get('subtype')
        site = bid.get('site')

        data = {
            '_id': _id,
            'area': bid_area,
            'city': city,
            'publishtime': publishtime,
            'title': title,
            'subtype': subtype,
            'site': site
        }

        moenApp.send_task('bid.jianyu.require.detail', args=(json.dumps(data),), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
        print(f'send to require detail 1 次: {data}')
        # moenApp.send_task('bid.jianyu.require.detail', args=(json.dumps(data),))
        # print(f'send to require detail 2 次: {data}')

    if next_page and len(data_list) == 100 and int(page) < 5:
        moenApp.send_task('bid.jianyu.require', args=(json.dumps({
            'keyword': keyword,
            'page': int(page)+1,
            'area':area
        }),), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)

@moenApp.task(
    name='bid.jianyu.require.detail',
    bind=True,
    acks_late=True,
    rate_limit='3/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def require_detail(self, tmp_data):

    bid_data = json.loads(tmp_data)
    _id = bid_data['_id']
    print(f'receive data: {bid_data}')


    phone, cookies = get_cookies()
    if not phone:
        print('没有cookies了')
        moenApp.send_task('bid.jianyu.require.detail', args=(json.dumps(bid_data),))

        time.sleep(60)

        return

    headers = {
        'authority': 'www.jianyu360.cn',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    url = f'https://www.jianyu360.cn/article/content/{_id}.html'
    params = {
        'aside': '0',
    }
    try:
        response = requests.get(
            url,
            params=params,
            cookies=cookies,
            headers=headers,
            proxies=get_proxy_ip(1),
            stream=True
        )
        rds_206_11.hincrby('jianyu:cookies_count', phone)
    except Exception as e:
        moenApp.send_task('bid.jianyu.require.detail', args=(json.dumps(bid_data),))
        print('ERROR: ', e)
        return

    res = re.findall('<div id="tab1">(.*)<div id="attach-list"', response.text, re.S)
    if len(res) > 0:
        res = res[0]
        final_res = '<div id="tab1">' + res

    else:
        final_res = response.text


    if '<title>验证码</title>' in final_res:

        captor_data = {
            '_id': _id,
            'cookies': cookies,
            'final_res': final_res
        }
        moenApp.send_task('bid.jianyu.captor_cookies', args=(json.dumps(captor_data),))
        moenApp.send_task('bid.jianyu.require.detail', args=(json.dumps(bid_data),))
        return

    data = etree.HTML(response.text)

    res = data.xpath('//*[@id="tab1"]')
    if res:
        detail = res[0]
        detail = etree.tostring(detail, method='html', encoding='utf-8').decode()
        # print(detail)
        bid_detail = detail
    else:
        bid_detail = ''
        print(f'ERROR: no bid detail: {bid_data}')
        # moenApp.send_task('bid.jianyu.require.detail', args=(json.dumps(bid_data),))
        return

    res = re.findall('params: (.*),', response.text)
    if res:
        data = json.loads(res[0])
        url = data['obj'].get('href')
        # print(url)
        orign_link = url
    else:
        orign_link = ''
    bid_data['orign_link'] = orign_link
    bid_data['bid_detail'] = bid_detail


    moenApp.send_task('bid.jianyu.clean', args=(json.dumps(bid_data),), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
    print(f'send to clean: {bid_data}')
    rds_206_11.hset('jianyu:require_data', bid_data['title'], json.dumps(bid_data))
    print('ok')


@moenApp.task(
    name='bid.jianyu.detail',
    bind=True,
    acks_late=True,
    rate_limit='2/s', # 处理堆积的时候，把速率限制注释掉
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def detail(self, tmp_data):

    bid_data = json.loads(tmp_data)
    _id = bid_data['_id']
    publishtime = bid_data.get('publishtime', 0)

    print(f'{_id} : {time.strftime("%Y-%m-%d", time.localtime(publishtime))}')

    # 几百万数据堆积后，用这个根据时间区分开

    # if int(publishtime) < get_zero_time(6):
    #     moenApp.send_task('bid.jianyu.history_tmp', args=(json.dumps(bid_data),))
    #     print(f'时间范围之外：{_id}')
    #     return

    # else:
    #     moenApp.send_task('bid.jianyu.current_tmp', args=(json.dumps(bid_data),))



    if rds_206_11.sismember('jianyu:crawled_id', _id):
        print('爬前判断：已经爬过了')
        return

    phone, cookies = get_cookies()
    if not phone:
        print('没有cookies了')
        moenApp.send_task('bid.jianyu.detail', args=(json.dumps(bid_data),))

        time.sleep(60)

        return

    headers = {
        'authority': 'www.jianyu360.cn',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    url = f'https://www.jianyu360.cn/article/content/{_id}.html'
    params = {
        'aside': '0',
    }
    # Ipool.get_proxy_random()
    try:
        response = requests.get(
            url,
            params=params,
            cookies=cookies,
            headers=headers,
            proxies=Ipool.get_proxy_ip(),
            stream=True,
            timeout=15
        )
        rds_206_11.hincrby('jianyu:cookies_count', phone)
    except Exception as e:
        moenApp.send_task('bid.jianyu.detail', args=(json.dumps(bid_data),))
        print('ERROR: ', e)
        return

    res = re.findall('<div id="tab1">(.*)<div id="attach-list"', response.text, re.S)
    if len(res)>0:
        res = res[0]
        final_res = '<div id="tab1">' + res

    else:
        final_res = response.text


    if '<title>验证码</title>' in final_res:

        captor_data = {
            '_id': _id,
            'cookies': cookies,
            'final_res': final_res
        }
        moenApp.send_task('bid.jianyu.captor_cookies', args=(json.dumps(captor_data),))

        moenApp.send_task('bid.jianyu.detail', args=(json.dumps(bid_data),))
        print(final_res)
        return

    data = etree.HTML(response.text)

    res = data.xpath('//*[@id="tab1"]')
    if res:
        detail = res[0]
        detail = etree.tostring(detail, method='html', encoding='utf-8').decode()
        # print(detail)
        bid_detail = detail
    else:
        bid_detail = ''
        print(f'ERROR: no bid detail: {bid_data}')
        # moenApp.send_task('bid.jianyu.detail', args=(json.dumps(bid_data),))
        return

    res = re.findall('params: (.*),', response.text)
    if res:
        data = json.loads(res[0])
        url = data['obj'].get('href')
        # print(url)
        orign_link = url
    else:
        orign_link = ''
    bid_data['orign_link'] = orign_link
    bid_data['bid_detail'] = bid_detail


    moenApp.send_task('bid.jianyu.clean', args=(json.dumps(bid_data),), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
    print(f'send to clean: {bid_data}')

# 用于存老数据
@moenApp.task(
    name='bid.jianyu.history_tmp',
    bind=True,
    acks_late=True,
    rate_limit='3/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def history_tmp(self, data):
    data = json.loads(data)

    print(data)
    # time.sleep(15)
    moenApp.send_task('bid.jianyu.detail', args=(json.dumps(data),))


# 用于暂存最新的数据
@moenApp.task(
    name='bid.jianyu.current_tmp',
    bind=True,
    acks_late=True,
    # rate_limit='7/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def current_tmp(self, data):
    data = json.loads(data)

    print(data)
    # time.sleep(15)
    moenApp.send_task('bid.jianyu.detail', args=(json.dumps(data),))


@moenApp.task(
    name='bid.jianyu.clean',
    bind=True,
    acks_late=True,
    rate_limit='30/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def data_clean(self, tmp_data):
    data = json.loads(tmp_data)
    print(f'receive data: {data}')
    item = {}
    detail = data.get('bid_detail')
    if not detail:
        return

    _id = data['_id']
    url = f'https://www.jianyu360.cn/article/content/{_id}.html'

    item['uuid'] = sign(url)
    item['title'] = data['title']

    subtype = data.get('subtype')
    if subtype and '公告' not in subtype:
        subtype += '公告'
        notice_type = judge_notice_type(subtype)
        item['notice_type'] = notice_type
        item['bid_type'] = subtype
    else:
        item['bid_type'] = ''
        item['notice_type'] = 1

    item['bidding_type'] = ''
    item['invite_company'] = ''
    item['win_company'] = ''
    item['agency_company'] = ''



    pro = data.get('area')
    if pro and pro != '全国':
        province = single_province(pro)

        item['pub_province'] = province
    else:
        item['pub_province'] = ''
    city = data.get('city')
    if city:
        item['pub_city'] = city
    else:
        item['pub_city'] = ''
    item['pub_district'] = ''
    item['pub_addr'] = ''

    publishtime = data.get('publishtime')
    if publishtime:
        pub_time = time.strftime("%Y-%m-%d", time.localtime(int(publishtime)))
    else:
        pub_time = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))

    item['pub_time'] = pub_time
    item['tender_time'] = '1971-01-01 00:00:00'
    item['item_number'] = ''

    item['products'] = ''
    item['money'] = ''
    item['unit'] = '元'
    item['notice_detail'] = detail
    href = data.get('orign_link')
    if href:
        item['url'] = href
    else:
        item['url'] = ''
    item['doc'] = ''
    # item['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # item['update_time'] = ''
    item['source_name'] = '剑鱼'
    item['other'] = url
    item['filepath'] = upload_us3(item)
    str_data = json.dumps(item)



    moenApp.send_task('bid.jianyu.zoo', args=(str_data,), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
    print(f'send to zoo: {item}')
    item['tender_time'] = 31507200000

    sf = SonyFlake()
    next_id = sf.next_id()

    final_data = {
        "version": 1,
        "trace_sn": str(next_id),
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+time.strftime('%z', time.localtime()),
        "data_type": "spider_bid",
        "data": item
    }


    str_data = json.dumps(final_data)
    moenApp.send_task('bid.jianyu.kfk', args=(str_data,), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
    print(f'send to kfk: {final_data}')

    #
    # else:
    #     log.warning(item)
    #
    #     raise ValueError

@moenApp.task(
    name='bid.zhiliao.clean',
    bind=True,
    acks_late=True,
    rate_limit='30/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def data_clean_zhiliao(self, tmp_data):
    data = json.loads(tmp_data)
    item = {}
    detail = data.get('bid_detail')
    if not detail:
        return

    # _id = data['_id']
    # url = f'https://www.jianyu360.cn/article/content/{_id}.html'

    zl_url = data['zl_url']

    item['uuid'] = sign(zl_url)
    item['title'] = data['title']

    subtype = data.get('subtype')
    if subtype and '公告' not in subtype:
        subtype += '公告'
    notice_type = judge_notice_type(subtype)
    item['notice_type'] = notice_type
    item['bid_type'] = subtype

    # item['invite_company'] = meta['invite_company']
    # item['win_company'] = ''
    # pro = data.get('area')
    # if pro and pro != '全国':
    #     province = single_province(pro)
    #
    #     item['pub_province'] = province
    # city = data.get('city')
    # if city:
    #     item['pub_city'] = city
    # item['pub_district'] =
    # item['pub_addr'] = ''

    # publishtime = data.get('publishtime')
    # if publishtime:
    #     pub_time = time.strftime("%Y-%m-%d", time.localtime(int(publishtime)))
    # else:
    #     pub_time = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))

    pub_time = data.get('publishtime')
    if pub_time:
        item['pub_time'] = pub_time
    # item['tender_time'] = ''
    # item['products'] = meta['product']
    item['money'] = ''
    item['notice_detail'] = detail
    href = data.get('orign_link')
    if href:
        item['url'] = href
    else:
        item['url'] = ''
    item['doc'] = ''
    # item['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # item['update_time'] = ''
    item['source_name'] = '知了'
    item['other'] = zl_url
    item['filepath'] = upload_us3(item)

    str_data = json.dumps(item)

    print(item)
    moenApp.send_task('bid.jianyu.zoo', args=(str_data,), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)
    # moenApp.send_task('bid.jianyu.kfk', args=(str_data,))


@moenApp.task(
    name='bid.jianyu.zoo',
    bind=True,
    acks_late=True,
    # rate_limit='30/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def keep_date(self, tmp_data):
    bid_data = json.loads(tmp_data)
    print(f'receive data: {bid_data}')
    try:
        if test:
            # 测试库
            MyJyTestDao.upsert(**bid_data)
        else:
            # 正式库
            MyJyDao.upsert(**bid_data)
        save_crawled_id(bid_data)
    except Exception as e:
        print(f"error: {e}")
    print(f'save success:{bid_data}')


@moenApp.task(
    name='bid.jianyu.kfk',
    bind=True,
    acks_late=True,
    rate_limit='50/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def keep_kfk(self, tmp_data):
    bid_data = json.loads(tmp_data)
    print(f'receive data: {bid_data}')

    # print(type(bid_data), bid_data)
    # kfk.send_message(bid_data)
    # producer = KafkaProducer(bootstrap_servers=['172.16.63.83:9092', '172.16.113.148:9092', '172.16.135.145:9092'],
    #                      value_serializer=lambda m: json.dumps(m).encode('utf-8')
    #                      )
    # future = producer.send('spider-bid-info-v1', bid_data)
    # result = future.get(timeout=30)
    # print(result)
    # producer = Kafka_producer()
    # print("===========> producer:", producer)
    producer = Kafka_producer()

    producer.sendjsondata(bid_data)
    print(f'send to kfk: {bid_data}')

    # my_pro = My_Kafka_producer()
    # my_pro.sendjsondata(bid_data)


"""
93以前是ascii的
"""

@moenApp.task(
    name='bid.jianyu.captor_cookies',
    bind=True,
    acks_late=True,
    rate_limit='80/m',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 30
    }
)
def captor(self, tmp_data):
    cookies_data = json.loads(tmp_data)

    # print(type(cookies_data), cookies_data)
    _id = cookies_data['_id']
    cookies = cookies_data['cookies']
    html = cookies_data['final_res']

    # with open('./ccc.html', 'w')as f:
    #     f.write(html)

    if "<title>验证码</title>" in html:
        print('yes 验证码')
        # print(html)
    else:
        print('没有验证码')
        return

    word = re.findall('请在下图依次点击：<span>(.*?)</span>', html)
    if word:
        word = word[0]
    else:
        word = ''

    img = re.findall('src="data:image/png;base64,(.*?)"', html)
    if img:
        # img = 'data:image/png;base64,' + img[0]
        img = img[0]
        image_base64 = img.replace('#43;', '+').replace('&', '')
    else:
        image_base64 = ''
    print('word: ', word)
    # print('image_base64: ', image_base64)

    # 看看image_base64类型是不是正确的“bytes”类型
    # print(type(image_base64))
    # 解码图片
    imgdata = base64.b64decode(image_base64)
    # 将图片保存为文件
    # with open("img.jpg", 'wb') as f:
    #     f.write(imgdata)

    img_byte = gen_img(word, imgdata)


    data = cjy(img_byte)
    cross_car(data, _id, cookies)

def count_zl_title(title, date):

    if '_' in date:
        date = date.split('_')[0]

    key = "jianyu:zl_title:"+date
    rds_206_11.sadd(key, title)

def count_keyword(keyword, count):
    date = datetime.datetime.today().strftime('%Y-%m-%d')

    key = "jianyu:jy_keyword:"+date
    rds_206_11.hset(key, keyword, count)

def upload_us3(item):
    uuid = item['uuid']
    text = item['notice_detail']

    ufile = UfileOss()
    if test:
        folder_name = "other_test/"
    else:
        folder_name = "other_bid"

    for _ in range(6):
        try:
            file_name = f"{uuid}.html"
            result_file = os.path.join(folder_name, file_name)
            ufile.upload_bytesIO(result_file, text.encode('utf-8'), mime_type='text/html')

            return result_file
        except Exception as e:
            time.sleep(0.05)
    return None

class UfileOss(object):
    public_key = '4eXwD7vhEE5Ln9TGMvGARl30U9dau3Zq5'  # 账户公钥
    private_key = 'KK64s7lhLtrHx50cbD02cB1yli6DRguJwIHz2jpQ0x38'  # 账户私钥
    bucket = 'useful'  # 空间名称

    def __init__(self):
        self.ufile_handler = filemanager.FileManager(self.public_key, self.private_key)

    def upload_file(self, put_key,local_file):
        '''普通文件上传'''
        ret, resp = self.ufile_handler.putfile(self.bucket, put_key, local_file, header=None)
        assert resp.status_code == 200

    def upload_bytesIO(self, file, content,mime_type=None):
        '''二进制上传'''
        bio = BytesIO(content)
        ret, resp = self.ufile_handler.putstream(self.bucket, file, bio,mime_type=mime_type)
        assert resp.status_code == 200

def gen_img(word, imgdata):

    img = cv2.imdecode(np.frombuffer(imgdata, np.uint8), cv2.IMREAD_COLOR)
    # # # 将bgr转为rbg
    # imgBGR = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    imgBGR = img
    # imgBGR = cv2.imread("img.jpg")  # 读取彩色图像(BGR)
    blank = np.zeros((50, imgBGR.shape[1], 3), dtype=np.uint8)
    h = imgBGR.shape[0]
    imgBGR = np.concatenate([imgBGR, blank], axis=0)

    if (isinstance(imgBGR, np.ndarray)):  # 判断是否 OpenCV 图片类型
        imgPIL = Image.fromarray(cv2.cvtColor(imgBGR, cv2.COLOR_BGR2RGB))

    text = "请在上图依次点击：" + word
    pos = (0, h)  # (left, top)，字符串左上角坐标
    color = (255, 255, 255)  # 字体颜色
    textSize = 20
    drawPIL = ImageDraw.Draw(imgPIL)
    # fontText = ImageFont.truetype("./font.ttf", textSize, encoding="utf-8")
    fontText = ImageFont.truetype("/root/other_bid_project/Muto/plantform/font.ttf", textSize, encoding="utf-8")
    drawPIL.text(pos, text, color, font=fontText)
    imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)

    # cv2.imwrite('./test_result.jpg', imgPutText)

    # with open('new.jpg', 'wb') as f:
    #     f.write(np.array(cv2.imencode('.jpg', imgPutText)[1]).tobytes())

    return np.array(cv2.imencode('.jpg', imgPutText)[1]).tobytes()

def cjy(im):
    chaojiying = Chaojiying_Client('qi2017', '316952817qwe', '901155')	#用户中心>>软件ID 生成一个替换 96001
    # chaojiying = Chaojiying_Client('useful', 'useful', '945901')	#用户中心>>软件ID 生成一个替换 96001
    # im = open('test_result.jpg', 'rb').read()													#本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    result = chaojiying.PostPic(im, 9103)	#1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()
    # data = json.loads(result)
    pos = result['pic_str'].replace('|', ';')
    print('pos: ', pos)
    return pos

def cross_car(pos, _id, cookies):

    headers = {
        'authority': 'www.jianyu360.cn',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'app': 'jyweb',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'SESSIONID=8ee36e64b75ee1e4392990633ca186a69f5ab506; SESSIONID=8ee36e64b75ee1e4392990633ca186a69f5ab506; Hm_lvt_52c42de35032567eb9d7a24a43c84bda=1672732558; c__utmc=875156445.306608062; selectNum=1; ud_safe=QlxIWlxHUVMCVhYNSV1dRFNTAFEQW0Vd; device=web-9b97b46e-e003-41dc-9a1f-3fe51aa8d7d5-1672742917066; c__utma=875156445.306608062.281617177.1672812352.1672818613.10; Hm_lpvt_52c42de35032567eb9d7a24a43c84bda=1672818661; c__utmb=875156445.306608062.1672818613.1672818660.2; userid_secure=h2RKImWxeUBcOi4kZiCEKCYideYzEWG3JGKdDEKTrAiI0NT6tvjknNrv5jlhBPszCmky9c4PDL7nz9VSpF+326I6jyDgERxr4TaAwykuivQHuLJMixoleapo+hyesIJ8XkXccO+p3XOiGUcN9jXnQgB15c+Cq0iOfMTprwwRlX6+7aFRRtPryag0ssS9cl6ehFUDGJvwzO7Qo4oyrfEAMTDb6LLMopoz06tTI2GJFk1DkXxjl46U9W8mtXm29QMWUmbDNJK/uYxDwrR3DjrWWaNc3GHV+HZuf0lX3NPrZETnMx0SIqEvJNZHf0ThsKjFhWX1oLmdbjDjmjcUwZMLLCoqKjIwMjMtMDEtMDEgMDA6MDA6MDA=',
        'origin': 'https://www.jianyu360.cn',
        'pragma': 'no-cache',
        'referer': 'https://www.jianyu360.cn/article/content/ABCY1xGZDI4IywsI3hlZAckDDMZDSdgV1VjK1gsPS43Z2BzYCtUCUI%3D.html',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }



    params = {
        'kds': '大数据',
    }

    data = {
        'antiVerifyCheck': pos,
        'imgw': '331',
    }

    response = requests.post(
        f'https://www.jianyu360.cn/article/content/{_id}.html',
        proxies=get_proxy_ip(''),
        params=params,
        cookies=cookies, headers=headers, data=data)
    print('发送验证', response.content.decode())

def sign(data):
    str_md5 = hashlib.md5(data.encode(encoding='utf-8')).hexdigest()
    return str_md5

def get_cookies():
    for i in range(50):
        phone = rds_206_11.rpop('jianyu:account_spider').decode()
        print(phone)

        number = rds_206_11.hget('jianyu:cookies_count', phone).decode()
        if int(number) < 1500:
            rds_206_11.lpush('jianyu:account_spider', phone)
            cookies = json.loads(rds_206_11.hget('jianyu:cookies', phone).decode())
            print(cookies)
            return phone, cookies
    print('没有cookies了')
    return None, None

def get_proxy_ip(key):
    num = random.randint(0, 19)
    # print(num)
    field_name = f'ip_{num}'
    proxy = rds_206_11.hget('ip_pool', field_name)
    # print(proxy)
    ip = json.loads(proxy.decode())
    ip = {
        'http': 'http://' + ip['http'],
        'https': 'https://' + ip['http'],
    }
    return ip

class Ipool:

    @classmethod
    def get_proxy_ip(cls):
        num = random.randint(0, 19)
        field_name = f'ip_{num}'
        proxy = rds_206_11.hget('ip_pool', field_name)
        ip = json.loads(proxy.decode())
        ip = {
            'http': 'http://' + ip['http'],
            'https': 'https://' + ip['http'],
        }
        print(ip)
        return ip

    @classmethod
    def get_proxy_ip_dm(cls):
        num = random.randint(0, 33)
        # print(num)
        field_name = f'ip_{num}'
        proxy_ip = rds_206_11.hget('ip_pool_dm', field_name).decode()

        username = "18923881404"
        password = "pachong,1234"
        ip = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
        }
        # ip = "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
        print(ip)
        return ip

    @classmethod
    def get_proxy_random(cls):
        num = random.choice([1, 2])
        if num == 1:
            return Ipool.get_proxy_ip()
        else:
            return Ipool.get_proxy_ip_dm()


def in_limit(dt):

    today = datetime.datetime.today()
    limit_date = (today - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    # print(limit_date)

    limit_timestamp = time.mktime(time.strptime(limit_date, "%Y-%m-%d"))

    # 转换成时间数组
    timeArray = time.strptime(dt, "%Y-%m-%d")
    # 转换成时间戳
    timestamp = time.mktime(timeArray)

    # print(timestamp)  # 1672540205.0
    return timestamp >= limit_timestamp

def save_crawled_id(item):
    url = item.get('other')
    if not url: print('error: no url')
    _id = re.findall('content/(.*?).html', url)
    if _id:
        rds_206_11.sadd('jianyu:crawled_id', _id[0])
        rds_206_11.sadd(f'jianyu:crawled_id_{datetime.date.today()}', _id[0])
    else:
        print('error: no id', item)

def get_zero_time(num=3):
    """
    生成某天23:59:59秒时的时间戳
    :param num:
    :return:
    """
    # 获取当前时间
    current_time = datetime.datetime.now()
    # 计算前天的日期
    previous_day = current_time - timedelta(days=num)
    # 设置时间为前天晚上23:59:59
    previous_day_midnight = datetime.datetime(
        year=previous_day.year,
        month=previous_day.month,
        day=previous_day.day,
        hour=23,
        minute=59,
        second=59
    )
    # 获取时间戳
    timestamp = previous_day_midnight.timestamp()
    return int(timestamp)

class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password =  password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def PostPic_base64(self, base64_str, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
            'file_base64':base64_str
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()

def test_captor():
    html = """
    <html>
<head>
<title>验证码</title>
<meta http-equiv="X-UA-Compatible" content="IE=edge,Chrome=1"/>
<meta name="renderer" content="webkit">
<meta name="viewport"
content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
<script src="/js/jquery.js"></script>
<meta content="telephone=no" name="format-detection"/>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,Chrome=1"/>
<meta name="renderer" content="webkit">
<meta name="baidu-site-verification" content="cSFG2PMaYX"/>
<meta name="applicable-device" content="pc,mobile"/>
<link href="/css/bootstrap.min.css" rel="stylesheet">
<link href="/css/bootswatch.min.css" rel="stylesheet">
<link href="/css/font.css" rel="stylesheet">
<link href="/css/jy.css" rel="stylesheet">
<link href="/css/common.css" rel="stylesheet">
<link rel="stylesheet" href="/css/unicorn.main.css"/>
<link rel="stylesheet" href="/css/unicorn.grey.css"/>
<script src="/js/jquery.js"></script>
<script src="/js/n_rem.js"></script>
<link href="/css/pc.css" rel="stylesheet">
<style>
body {
min-width: auto;
}

@media only screen and (min-width: 1200px) {
body {
min-width: 1200px;
}

.verify_logo {
width: 350px;
display: block;
}

.verify-body {
width: 350px;
margin: 0 auto;
text-align: center;
padding: 134px 0;
}

.verify-content {
border: #F5F5F5 solid 1px;
margin: auto;
width: 260pt;
background-color: #FFFFFF;
box-shadow: 1px 1px 1px 1px grey;
padding: 10pt;
display: flex;
flex-direction: column;
}

.public-nav {
display: "" !important;
}

.j-bottom {
display: "" !important;
}
}

@media only screen and (max-width: 1200px) {
.verify_logo {
width: 7rem;
display: block;
}

.verify-body {
width: 7rem;
margin: 0 auto;
text-align: center;
padding: 2.38rem 0 0 0;
}

#antiimg {
width: 100%;
}

.verify-content {
border: #F5F5F5 solid 1px;
margin: auto;
width: 7rem;
background-color: #FFFFFF;
box-shadow: 1px 1px 1px 1px grey;
padding: 10pt;
display: flex;
flex-direction: column;
}

.public-nav {
display: none !important;
}

.j-bottom {
display: none !important;
}

}

.public-nav {
border-bottom: 1px solid #e0e0e0 !important;
}

.fr {
float: right;
}

.logo img {
width: 74px;
}


.verify-content .word {
text-align: left;
}

.footBtn {
margin-top: 5pt;
display: flex;
flex-direction: row;
justify-content: space-between;
}


.j-wx-code {
width: 335px;
height: 355px;
background-color: #fff;
-webkit-border-radius: 6px;
-moz-border-radius: 6px;
border-radius: 6px;
position: relative;

}

.j-wx-code > .code-close {
width: 40px;
height: 40px;
position: absolute;
right: -20px;
top: -20px;
cursor: pointer;
-webkit-transition: all 1s;
-o-transition: all 1s;
-moz-transition: all 1s;
transition: all 1s;
}

.j-wx-code > .code-close:hover {
-webkit-transform: scale(1.2);
-moz-transform: scale(1.2);
-ms-transform: scale(1.2);
-o-transform: scale(1.2);
transform: scale(1.2);
}

.j-wx-code > .code-title {
height: 82px;
background: url(/images/j-wx-code-title.png) center center no-repeat;
-webkit-animation: moveYun 15s infinite linear both;
-moz-animation: moveYun 15s infinite linear both;
-o-animation: moveYun 15s infinite linear both;
animation: moveYun 15s infinite linear both;
}

.j-wx-code > .code-wxm {
text-align: center;
margin-bottom: -6px;
margin-top: -16px;

}

.j-wx-code > .code-wxm > img {
width: 200px;
height: 200px;
margin-top: -5px;
}

.j-wx-code > .code-text {
text-align: center;
}

.j-wx-code > .code-bottom {
width: 470px;
height: 211px;
position: absolute;
bottom: -113px;
left: -73px;
background: url(/images/j-wx-code-bottom.png) 0 0 no-repeat;
}

.j-wx-code > .code-bottom > img {
position: absolute;
left: 280px;
top: 88px;
-webkit-animation: codeWxMove 10s linear both;
-moz-animation: codeWxMove 10s linear both;
-o-animation: codeWxMove 10s linear both;
animation: codeWxMove 10s linear both;
-webkit-animation-fill-mode: forwards;
-moz-animation-fill-mode: forwards;
-o-animation-fill-mode: forwards;
animation-fill-mode: forwards
}

#antiVerify > div:first-child {
display: none;
}

#antiVerify > div:nth-child(2) {
max-width: 360px !important;
margin: 0 auto !important;
position: unset !important;
top: unset !important;
left: unset !important;
z-index: unset !important;
transform:unset !important;
}

#antiVerify > div:nth-child(2) > div:nth-child(1),
#antiVerify > div:nth-child(2) > div:nth-child(2),
#antiVerify > div:nth-child(2) > div:nth-child(1) > img {
max-width: 360px !important;
}
</style>
</head><script src="/antiRes/js/mainHook.js?v=4"></script>
<body>

<div class="verify-body">
<div id="antiVerify">
<div></div>
<div style="margin: 0 auto;max-width: 360px;">
<div style="width: 90vw;max-width: 360px;">
<img style="width: 90vw;max-width: 360px;" src="/antiRes/images/verify_logo.png">
</div>
<div style="width: 90vw;max-width: 360px;border: #F5F5F5 solid 1px;margin: auto;background-color: #FFFFFF;box-shadow: 1px 1px 1px 1px grey;padding: 10pt;display: flex;flex-direction: column;">
<div style="margin-bottom:8pt">
<div>请在下图依次点击：<span>鐿誋箺</span></div>
</div>
<div style="position:relative;width:100%">
<img id="antiimg" onclick="antiAdd(event,this);"
src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAUAAAABkCAIAAAB4uH5pAACAAElEQVR4nGy9Ways23YeNPu/qaq11u5Odxv7duE6Uow7IpvAJZ1ikpgkIjh0ipAfyEMEIUhRnpDyggISLwgkUB4IoDzwghBSFAVIIC0EOyJRbN/ccO1rH9/u7HPOPnvttarqb2aLxvjmP6uOQ&#43;loa5&#43;9alX9//znHOMbY3zjG&#43;bmD/5rUkpVRAgh&#43;ZBzdlIbYzL/XcYspZRC5Jzj6kMIwWShlDHGWuv6oes613fGmPe/921RipBSaa2d01pnUXLO4v2P4roKKftxNMas6xrWVQghpBQSn03vEynRfzkLLYQxwlrjnFFa8FcXfg3DYIyJMYYUlaLvkVIe16WUIhJ/QsxC0tVrrUMIWmvTOeecNDrGeF4XsSz0zlJELvRnEUIpKZRSyvFvSSlzzmsIMUYh&#43;SKnk7BWdE5ozb9ShFJCK7pUY&#43;gf6V7oD7qAEMTs6T14aUVvUIq&#43;xVm6TfzH30k/klI4a8dxGIZSyvl8zuczfUj9dU1frTXfWqQ3GyOPcwlB&#43;FDfoFT9TLwNl2cM/SnoandLTinFlGipNd1pLrSkqWT&#43;BKONkabeOC31utTrl1JYY52zHT3NGKP3Pq&#43;hxEhXGAKtIX0p37zCBfMlOSuM6YY&#43;xlh8zDHScylF8mMUY&#43;Jrk/QtkZ8aVivy9eDvdXGUVEpZI4Qw1g7jIKRclmXxK/2WoP2jBL3FKdqxRtHtnUoopWRR6H55k9BPlOr7flmWdZ5zzp2iZ11yTjH5zNtQ05bW/DRjoQudTidpDH638FZV/JKZLlFn3jRCxBjj4rHZ6BsNb0tNV1KMklK&#43;EYvQWkmdUxKrp&#43;eY&#43;QZDFNZIa/H5fNf0FYbPjtUm5xzW1XtfQiyl1JPCf7Fd1/e9UCqlKN3v&#43;Rm6SUlPoMSUc9Z8S48vP6RHWOoy0SIquqDgBI5T3Tf0sPmWntxa67q&#43;t9ZmKeZ5nqeTmOdnZVyWJedsrRVC0CbIWSk1DAMuSHz6NcdV8RfxAsn2Hu&#43;9UopOLx3CSCe867TWw&#43;1NSimsflkWMS20sa4/U8m6pWivS1gNa&#43;3O9c51Mhfv1zAt3vu4et60kh6/rA9VKbV/ekfXw8&#43;ynnBeAH4KqpQSY8Rh4GOSuizZuBh659XnSEmfQadFSp/iSq&#43;FToXRZOaEcM71vHo4S&#43;1PKSUOTylFKZU&#43;ek3XSee0rhIum26B34ajrp3rRzKv6YNP6LjidNKpKWy76B7ZwPX0pT2tJP1jziXRAUj88pHuiO4u53G/jzHKRJekJX211cY5NxTVVixaupgo6NdDoouJ8xpjNGTrTG9os&#43;bP3NC3xFRKMfTBWfCXpIVusODvsOaJN5jRdEelsFknw6Sc7brOSPrewjcm&#43;U/BBiIPFmtOj5I3PZZ3GAbnXGdtCGF&#43;PE3TlEKkXd2PtIxGW37RGdZ0F68&#43;&#43;gi7hf5Tkr2SM8aEhQ5VnhZeZ6WsdZo2xrqu1Q8YI7FPNH/7ixtjTKfIDJUQ24Fc51mxZaf3sLmRmg7/NM9SKcNbK8eUU5K54EHTTYZAy&#43;JsNwzK0COT4ss/Qpsb/xW6XbINOY8vXpCPlTqltM7LPM/Ze/qpzHxL5IVgaQTvJKHoYBhHpzSEQMdpnoX3QpnqPYZB8xL0fT8M4zxPOJnYNynVPeYy/W/mBwnfiw3K/ka3/ar5QOacl3mulhseVUpYYsGfE1Pkx5/hT/gwG/44&#43;kCVSiL/QJ5/2O9p22XaWGL7fMmfBoPFR5iOX6SLTcoanLEYyb/gbNPbkmi2PPGtwGqWUrA5aD3XNdbFlEY57DBNhteUUugZr6vsupISvcFayaerGrWcgFvogHmfsbmF0M7t9/ubm9txGHLO87LMy0zu4c5V10Gmh//k&#43;7p98qQaOCECX9K8erqqeRLwsYAYw9Dvds65wPhLxEgYiy2k1YTCXudFBC8y3bbYjbbvi624yVo7dASBTOYtcZrWdXWvpxhDjkkp1VlGarSGgeyplIkNQWaPVNjc6FhwwJRSPsUQAgyZ5efC&#43;4SeIJseWmofvNgOQwHE43uMx6Mcx92wo7/7tZTSk8HsP/zud/hBMOLQegMv1TqXzKiQ7taazlnr5l6JyAio&#43;VJyNPJwe7euq5/OYl2FUWIY3OHQ9/36Gy/parVRShtB20Cy8cIS0dXH6BMdaXhgxSdIZTKCme9LJbqPME28KIwBDV&#43;nINgsze/4fbhc&#43;hogIT5K548/5jup/9JA783dgVY8p3bkqr9bZtF1djf2fW&#43;MBZDQWvdSL&#43;xuvF&#43;XZUnrSldg7eFw4B0J8JYCv8ha80Xj&#43;OGsYvPRmdmgOw5S4Mdp2ZNLHPtAz1PxBYXV04FzbFPZvjr2bw/TkZZsWWk7hgQAprXGUoacaDUAgaTAttiABq8ArSDgeqgYWDDm7ztFaypsltWVlZLqO8kg6v0eB5gOPGCCIQ/mj3PPEFpKuYYKxmAC4FQZXea8roz/E5mh6hYUVge2I6VkGuTjV&#43;ZrDs&#43;GtoAJ2w449eGRLrvrRN/XAEEqBrppHHeH25v9fm&#43;M8d6fpokDH7q2EgK5x5gKILRS4qbn0EkI68TYO&#43;eyYT/sPV2t93S8Vzajno3CwrEGw2/JBr0aPkPGK1STd0F24rywERmd65IoIfgKTDZDn&#43;GrGZXQP0f&#43;FnwCogkYbn4KdSfjJHAscfv2OzGGyBilWjpeTworKeYpm8MwmvdSPHQNKWRPOzBHumoyeXguuBTawxTRqKCxnwmz8Ak1RQK4wS0p9oX0xK3R2iAiYUyRYJJUKrDv7cwLRoRF0TOV9sd&#43;Tzsq2AGan3fXdd77sJCtcmzdd2yJl8dHsut4eQJI&#43;HXAP&#43;ecEGJd1/P5TFiXPH51nrquS/2WEMIlrsBtszd&#43;WCa8jfytqQEMQUd2OECSGviaX5mjjo5PNf7dsVFY5wU7I8a4hnoSpJSLYovOthDrgdjb7naF3Rx9Y2fZftPP54/v61MhsBcR5wsp3WGPa0NsaTmYgUXzBLJon&#43;ntAmrQ2BNuRyCA50eXe7PH0nnvp5Wu&#43;ebm5vb29v3336dvtGYYx27oAaTpIH/3Q0K1JUsGdYDcQODee/LtMZItttYxZL3/6GUNlbcti1BieP6C7oltTaS9kkQi664Hy4d/M1stHgmRF4p9Ti5iO8BWsEkdOjrtIvMjWkWMahw5&#43;uVjw1kTy2Yxr4wgSvWxvCE0fC8BS4nInE&#43;CYfs4du1ZiJyVMR179bR6xJ9kKQJgCP1WJ&#43;nAhMTfqzYPSe7eSY6ehmEY&#43;76Ussy0hcN0pqO4pQ&#43;QQFFK7W4O2IT4XwbkdIWHHSG1zGA4cYgBcLQsS3tzIqgb1kgOaa8JYRX6jw/uBvudsW0FsMOBFJYYEHURaJccV7OLNLxtpoW8oVCSIgIOfKT44o9f3AtDCMV7kdcl1KWpAJsfJ7xHvWFJFo5Bf5mmmntgz1A/UAg5&#43;Rr&#43;4fnliiqNMQ05Y6UQgSRTzzOWrMXA5HLZ/FOEKauToW3NT6ceFU9LVjgE6Lq&#43;OqKcC&#43;I9fkUHrMp2oQicpZTSBIjCC1f4h4h1397fwVjARQMJ0&#43;fk1Fwf0h6EwH1wnfNwVqXY7ZZjjBS2sYmpqJvtvdb6zHuZ9kGMFNtvq22GgWytVs45bU2Nb1P6zHBDRyTUkLi61pSWZcE6O1dzTss0x3XVzuCLOChgnM8x&#43;bR6&#43;nX&#43;EWI8qem5L9MjxYKcmKQIZVmmaSrei4Whk1AEJgXH5xyHj6UmbOiM870UrbTRx09eiy2NpLF1&#43;TplxPO6iv1oa2gA&#43;2QZUHR0CcpZbfTCoS25uoXDTrLWfKQZbeWVMUUE0IWdZZ/Gn1mMAhKhZ9F3WC4&#43;9gxn2LjI3VhaAnXDNdV8bKiT822RoESMwnW8z0216fjFUsxuRw8xAOOIS&#43;ZlWmWF0LSNKmrIOZ6nihSaoQRc7zv&#43;3prGo2/ntKvk05H5OBQ6dgYhpBSf&#43;7F6Pums8wXhur2nw&#43;mcck5o2naCEySqHy4ZIn4ZTmlQmMQvOmNCAuvSBt3XDQR/xWBwhYMq8Gktd8pr95be4ZDTwWBgg&#43;MR2XAYTQZYS4WTT5D16YHiatdxhKoqOhLi4f4NYXI&#43;S3gnXm43NOgCV49ISXNMCyubNutAW2pecTE1ucIemN6ZEkLT6mRg1EIQL54hKdvyc0jFKd70IjEEIuegLBs1fT/Rl6mKONjVxfpNpSijh2HoOtp8mdPlJxG3FLXGNSc2UsuyMHar&#43;KIlLXu6rvqKBd/OfnjoNcM2DhbYyfDB9sgpYSPCoPB96MMhpaQjWQ3Nn2kEZwo&#43;OdGR4NBDWno6diRAcXd7Oy/LdDydz2e/rA3oVr/KoNSKC/6KMGRYf8n4kyGo6AfBHgW3DMSRUnJ8hAzbeM3JBvi3wZD9Uh0hsqLpAAc&#43;Ncd5qokAfppa67Hrh2E4v37dHEnZYGAz/a0CwvmjQI94Cda53tW0HxwAmZjzWTACxRUC95FRduISWhdxqR1sAa3U2rotfyZEVKLF84Z3Dg58WFZaWzZD2KV02HyQz/75PwxMUkqZ12We53Vdc8pxmqojTbyULcQv1SxhTctWHijwzFzqsNq0skTuRTVs7KvpPQuXc5y7FDxgO/DfGy5j4Eggb6xVtYIAS/R3USPPrhOCY1HF2yKmihpyph8hhFHkNCSvDterIsoznBNGqokfVYoCMAbfrpTk93RSMypca16nGV1yj7peGBYHd6El3Zq1AnFRjHRtWovzxPGY084prcg0JQKue8&#43;FqxiS95d1Rs4c8Wp72JKf/c0oWpIsp/oVsFCXlSz1rq3VXA4kPE&#43;YjO4oc/oHxSHJptlTVB4SHxg50C4chqHve8VJNcR7969fEyhbt0iS1lZqY26igk&#43;gDc0putM6Z2Q6jOn5kDhDsDxxjkN2PUwYBTuSt2ykSHK8PSBboZRaFXlrz1n9hbOyBfYRux&#43;GUtExsGx1NHm&#43;kILPMY7dSJcsOTOa48XLOdNQYV1PFBTTluDYwHZ9pnjKvBPIjfEBowDHdHwvESkbRCvW2mVZmkvAuUjAZXcjzjmtSaC9x1ncHifQr7VqcMGtTldMAbwD9F6KZfQUMjt5TqpZh3z7D/0u4CtgHHoWuuZFyE2zDUPwuTlnOjmGa0IpxpJzhWFIOLHtV9tLSnlQDjfQ0lSwan6e6GY4EmipWoLuJdUVRyykDdlsbOJafszsz7Yzb0XzuhWK4L94ddRzqWtEy6TrQ4Vp2FL5grOXwtIZo&#43;NnrcS/K3Wp3169&#43;sMBoIjdFdeNcQ1hqR&#43;I0JfMkKbP7PpqGhpgwwcahULFxcZxSIIsNxaHjEuq6VCZeTfXG&#43;OD6qxhH8VPka4HCZ5lmsU0iWnFXdBnan5qKXAele9X6avUC19O1BnulAOblmtQqaDcSF&#43;U4SXIMzzsucCjZI2uDT&#43;vUsQw0Ld7z2CyE9vniH1Py5vYjqNmnnhZjqdLUNY5MoIMQc0jeR7UaVbvldZj3xtjhq4HGF7mJSIliU2PJ1sr7Zf7Evsdr3yslee2YbSs3kJruSUySkrWOqBIZDdwOuh&#43;w1yfILsQ3XWGzSKyGMvUijVbCSqi0CxbcauVBjODbbM5bez//dM7xnfZex&#43;5ZFW4dBeWlS5DVbRIHhcQ&#43;p1/6Y9hozDGSvyJthVC8haFIgJMKa0xtLuSVwHqNE2/qfyDH41F4&#43;i26BF7Aic58UJYa/f7/eFwGIchcMwTMn3dHDzivcTOyvW9M5ZswbRwOoFeH8e5Wgv9qWSY5WISKpYiXa4nnGf6XhwAThvgZ/vbm5ZdBy5CfksPQ80xbGV0Q8tjahCeSwvjkR4fn93VgHOrq4NscD6dLG&#43;7vu&#43;llOu6no&#43;naZoWUSkW7SlE/sDEpamaOBDVtpZSuihQciAjy&#43;mfULEe2/vVl2WpmYuURfBdtwMCpNWg5&#43;5UR88ucBYtw13gETN47F6fL26EQXvdDCHhfkFj4GdND/vVE2N4EyO6po3BpgdZw2rdFjIiu/3&#43;5uZmOVBE0GlaQLEEOpZvjqfTCe&#43;hwwaeDF0AGeJD1Ej7zfOcG8WlFDEvwqIUTZCmJYcQGSaOrrNRiKWNMaeJ7gsHQF0RBZwsrdjRblZKeT6eatyxpWnxnrLrrl1UKxaup5P8/4PWtly4DDVpx2u7riuiZYU72PIU2SgUkJDtx5mi58LbDjVqyZkRyfhRiq/&#43;zpZhqsFq50B4wg1g4xPQ8p5WkCOXlqxr/hMg/LpyC3sTu&#43;rMAdQRrS3LYq1tR&#43;WCn3MWZ2ZZkVOxwjFjRskWtWpU0kJCEkVKOTy5oUUUNZtKxxvZ2sdH0dI26QI1tekJ9nSOgAwXvXRHy/fRRx&#43;1h4ocaSUXHcZKz1rXaZoIS3PyxnUOdUh6TrDHCjynBISCzHlCkI9Twiyxvr&#43;cYe/9bk2oal6g12YBW&#43;oeeS9siKMjU6U7N47jsN9Za9ccvfcz18MLIXEvEwFmZOPzJ28Q1fPN0IYG2ebFe&#43;/llFGKW0JclxWGUj0dOZnAHJVChsn19OAe7t8g&#43;0oBJOfvC&#43;elbRC0/6yBEUFqiiJkxmhIqsFqw0097vU8z9PrB3E&#43;iyh01x20o0uLGTykvu&#43;7HQF47XgNtfTeT/xaYsA&#43;RDGClqiIVkDScLWWC8t8JUXTxpO27iKkLbGY9Lv8vGKMNXXMZTb8SCm12&#43;1oxbd/aUnWmvWMoWGi6uGdE4RxuGjkK/Ky1t4K24xjPcCMTIf9znufmFGHSxLIZgv&#43;O/&#43;vamVd&#43;HwkkrGjQGXImQ4wHGOrMmXmFUnmml1SZO03XfepmKGW1DjmlJdsL&#43;IrKeUpzAKkjpQIO42j2vG2W1ewW5CebaUp/WYGFY6DKCWNUfwA/OlEV2XsOI63w05rHVa/ruuj542rZOM8wcq99dZb7JUZ/Piweo8E20E55hgFOFnaEPnCGKn3UsEYA&#43;/k6bIJ0TnUyfqus9ZWO1Uu5XiYai9ys&#43;IIHHI1HDZtqU7NWxnmb5gDDkaLL3AMCgXP6hL&#43;4b9SRMf8yrEXw2D3u77vkyzYhbQ3sqDdPTGFJtDXOc7KSt5YIXO9BNAOYQV8ndS17lqKsBz1SVHhqFIAtMPdEzCokOen3cgLNgaBmmSj5azBh2UVpyMK/mIcjXMwQ&#43;yvOPuKWDqgrsG5TG0v2YShU32PGv5aUkboRIfEqr7HnY7jSAcJFTsgR0ZbuncgUTIikC0x9pnPfRYJIdhNcjn8NJdlwfMidDnNExe9afGRAypXsTFvLdf3cBW0u5ylCJ83MJ3GlDxTHnIgJzQy0Vg8TDjAQHyaDzlIKeD/VV6A97TrlBJWtcx2DRUZIKn9/sKmpI0hI5fZpfj8b6/xYXuVzaJcx/RlCyN9uiSrtboE37zhatG8pYJKUdq6DSSAoZVA90MWPm8UkbRxHlwnGgWys8w0cNKYu7s7stCCT8Vpnuc5rT7nPMiaacT1oIrLmTqJ6J9Ol/epJbekukpOUDDBBfTKo1KJwQ8fdVBKy&#43;iQExeNyMGXarseUIoeiZQtaamHTm5ffUlvciYIsAXZC66Q8/VYrtDGdLGVWM9hbIwxyWcDOYWb/S3yq&#43;QxmCyTNZ2N3Y6MGih7ggkGIhI4f&#43;zZw0jDHG&#43;yYp5DXAqXNK0XIR2uGFeY860PamW4OSlOLE2nUz0VMYrVV56WtaKzWAfnCBQ453wMgAOI2bz34XSiDTqO483NTZZkqqaF3jPjCdI1nM9nhGxSysSlvoTjp0tNo5I5MKLrJPvn&#43;XyWW2kQgRKSqYEpt0iywqwjZ7t4zzkaAYa2KMVwyLNuxD58AmwxZ5uXS26pXNIrasmt9AUyY0BuHyaGDzyuB0BddbaRajI/L5S4YDLqY2Vyq&#43;F82Mo7V6NmwfxwECGOD494Fl3Xjftd13WewwrywJe0SmWuOLUlsTamGwGnGgMk0eJJpLsA3g&#43;c1AFdPpXcYub54diCXjq65EUNsDQ&#43;pFVosYfO0wK6H8WrlQxDO7u/va01XiFcoe&#43;0vEyGfcKa2YMx5MvM53B93zBFCkzBB19HqrKxo6qZYC&#43;0f/IE6RkUDQg6chl/NQKHEHiBQDJ/43Q8tdybuSr3n/xyXbtuL8t&#43;2zp6nCv4tBynrY/3bCi12IxItS8h1vTbtZmjlaRTRyiJQE2oqZqU64YzbPKME9aOjqDvGznVYhZWEsaR9uVV0hVGDcnh1wtDhlQpe1tmfv/8OZPsmbLGmW08tU9ev9qyccYx35jMxDxXM6S3fF6MqEq6JRhjRkMrKWbCxmX2eFK035ztejbZUgZVOGnE1wNKbOI1GToxDFtgUi4uB1ECstzXFNrmZpDeZwO3ZUNFrVZUHoQRzFdHArbVk8BGxus2G2TI0VTDhpKjM95vUnKkwCUuZO&#43;va9FFiYZ61BU9FrxDzSduLlFpXYmiPuJgEwJFjgD9HezzF7&#43;u8yy/8Ef/JOArOXQfWrKkZ9gDxlIrJOacx2JhCWq4yCVvrfX940PjnSIpgvqtkFkNw&#43;FwGMcRuBEb3bNFhHVY13VZFkBcx6RjzURVPdCmF5bOxssPXi7zLM7M1OVggh5DjGMxLd2SLAeNTF3AYb72hLImpMulF0de6gqITFQkSyBm7nfBFrfqUo5CrYg98OHmttWizVWWC8sHCl491Zxq6rhykJHeKBkui040ADMWOdBSpIXA2GAdLrdFntis0&#43;MDgyM&#43;FUbR/tOStuPhQH96xkHsdKRgPLKsF1jOCEVyka926nTcPmF0u36DqEzUqmwjfpzZMFWOTb6Ai6FUlgtMfGu9gIfR1t7c3Iz7nRACe&#43;xU1jTPYloqr0trN4zjOMJkL5a&#43;YnWMSiRZrv7758ZOD7T80vZd3/fP3nqByB87h66cG&#43;HycUaqNbYDzAar4/VEyCO5Go/6qujdBWYK8U5v9tZ8L6payc&#43;l2eIftOmZyl&#43;Xu5VzB4UNHAXGjOCWZcH7c86KU31IXiouX0WsJ4d3uFPFTSzwvcmHWniDOd4MK7hESBXvhhEJM8LqAGuZ/JAUv&#43;33wjixKZDIoYPyggN/IfEjj3LyaFpo5L6MNqjO4QvKxmBABlsOLnpP/mFda9cbuvAa5aV5GDaQMnHZRqAOjCI4vXm4vR2GoTd2WZbT6zd&#43;mpQkOCE&#43;uofhIIgO0KVqTrVlcWHg5dVBrWCbN27lt/H&#43;0wklO26rZGjhtWgPviYbOKeNXhbkZszWlhRjBLuj8NZBsrJsD2yjW6XqLHD7jZ27AXIna9df68cCOx07LHNKSXKY4PbjbrcLIs/z/NFHHwVaZGbkZlEPsxCOuV9IzKDKmvGUcXXcToAItmKiacbKlFL8Rs8gQ7MbAKmQckMykr8xYnvA9KurmiIXPLjyLCr11xjzmGb2fsI410ndImrTd&#43;TTCoNzpwic91Yo9eLE68YfuErevoJsvF/mS6kGZoUX1XBSsEHcBqT9vCApVXI2m59USs1acnfNgCacP3JXfvqmfODLX/jO8m0vccDw6G1Jf/bw8Llw/1&#43;sL/5h2aHuzVuLAKwZBtBX0XVE26mQBZ/D2hpI0GCIvwe/8hPn/ZnYbcDijz3XT2ULiDKD2WWayZkp5iMyWnFDTyt/9/t&#43;brfb73ZkI&#43;fT&#43;Xg6orFuejyCsxrRfYpCGaNfepB4tF1NxvDzCxyj8j6euduGAY8d7pxzw83&#43;5ubW7gal1FI7F0KMIc/ee69WzkWzRfSaq03OtgIAPNjr169Tu5KYakcoCqcXRhv9izO2Mb&#43;lIWy/v7vVWk/LMk3nKYdrtk2Du5krlmqrALGFpsMmY6n9xmRWtvQ0GezIYJVTL&#43;eVk0Zgz&#43;fa3dJSQYbTTtMkxtHt9845ED81WqeLpbiU&#43;xZqMgwJ8yt&#43;a2WhAF077FcJ/05XTqFDHsZRc/UYEXJre9TCwlPR6pUrWA5wS5dWGxhLoa2fTlw1uSaHAEijpn3d14GO7pNv8XPizV7NEWO0Iltmv6Izod0FzNPKmAtRp5TduHv69Olg3Pl8Pj0eQwj9/Ykgq6QQpnTWWJM45jecRwQ2kTEjI02XY/Llu&#43;Q1HUgLZw0FAdrGi5/UTocQFr9yh0n&#43;977w5S&#43;a8LdP81/xHn3vOAXYJJ8v059//c1ftLf/ye1v8d5/YX38Q/7lX&#43;i/MKdCIY8xEtlHwT1kbNR2zgC70tWyg4lMc7h58gRxsuR7B0sv5/woo7S2P&#43;z2&#43;4NUalmWaZ1jJCsZl4WwIYg62/6X4of/wIXBU6mC5MGxl8GpqhW2re&#43;0kokpWlaNfRLCOs9zPJ84QUWfYAQ8m6nlctoKvGnYYtGeRhGfy3Mg6JVSgqpxCywc4urKFgYdj2&#43;bYwbFvCLV0jyCH2RNZizM6NJKWqs50VJTR2zXhTFKX3AjCh7X7LmW0TO&#43;sq9bXj2wh9e7Ho&#43;WrmTiLqKFznqypTWU&#43;8qboYP9zg98nqDdsp7P5zRNnPPgw8khSSu3NAZby8xXElg7NirVPAXXnWFcAA0ae/ySQyYLOjJ9mNv6bM3JM/f7nMjI&#43;taeIay2zplY2ycTh/o18sxZ7ve1dWbrmsbSPROuBSl&#43;I5YDg8jNoOC&#43;Klk/5OYboywgeFbmk/eEHfrOCBXBW5LyLhLQm2F2OY1QHJkGzyoReC5WKG00iJmPmlwLUGEGv9bWSjIzY&#43;kbtU8gKlJosJxR4FFK7fruT909s&#43;HxpZC/kdd/IOyD1F/K83vxGFNSmZ7CvxOnb9jDL9tDKeVnTu&#43;/8Od/3D39z9/7Sfj/zHUHWQTiI7rf4wPoEUhikZ8vteyKYKTVoZD0yk/2WhvVWe4JpaPrhmG/263eG613PcUbKpXj8Tg9Htd1keKL/0K1T10nup7&#43;AguN5gTEgaLyObiM0WMr09P1MwFjpBbgCWNoMgACRLbdbU1mOKd613Wd5EI/OEwicOwUaK/IgBatpcJmYy7teznLYaiJqGZruCXNcTYYPi2F6JdFLLTj1e1t6/BINRpnCu5pve5SbOV15NVauNje4AeHFvb2Spyw3D27o13L5R9FUVhQZ9rA83Lkj7POOSQwBJITb&#43;4vvoip6vD2ZLAqd1JdM8mevPMOCqelFO7uOq3c3dUpevCFozjJYB7XthyPlzqC3DyelGPs2DoyEg&#43;A&#43;Z4CBK7Dcyy8hRglcd/BhbveGsiA7jgpLluwgLrXMm6hUM2taiQywQtolXmxdSZZ2beVhNlCqz2KiCFc6qL4kHmd8G1VraW1c&#43;5G3u/oKChi43jvu32MceU9WSzdBRotUChVYE0zKUVzPT&#43;w/UNn7G/d3f3Ld5/9xdPLb6f1Z/n4/U&#43;dPJfyhfX0lbz8cpIhF8dI7cf0&#43;lvF8pfF/qydLOUX1JMA4kqItcKyUaFUrvEPip2VoFIZyo2UKupZo72dqgKMlMIzsjN8NrFzjDXOSSGC92JeRIxGHA74Ptn3A5rdPCG64a23uEIVwSVqz3LhmhueaBlHudvp2tDH/dGO/Mb6eF6WRclirT37XLtDjEZFDp0Mjr2HZhpW5wjNO3o&#43;Yrg9TNP0cHqkT9D6cHO4e/J0t9t9/PHHja6Ya2tOllL23AhexXdA2OTa2jRNKJpXHvHWG/Z0d9eaE2rUAf7turZM46WNqZSVw2Mf0xWkJKN2fPk9NjSWHhWHWQO3cDx7521U6pqH4aejdp//fMvMo6UheB/WVXRabJfIbtDCW0LwIARObwTONndddzjc6J7fn6tgzUZo&#43;VTSG3oUbLz8B4/MsBSNSYbWiLV2L&#43;lGvhc5cpd1QbWvRt1XiXQ61Vw7rYJK7EOiiWWrcrUDLKUkoIHyz9YBAgp6eFxEg&#43;gMhdAV3BhBtWWNq5Le&#43;8Lg2Q696yjypztio&#43;Cnc3UVSvWcNUAdOLx64LgaJE0VaVXRe4HMC50rw1gvorHeqpbL&#43;KHDM6XUN3t11ONfFuIPT/6LMfxNZV/K7rNp&#43;v1l&#43;m/lk/elFVn8RD4OKpi4/J3UccrwjXA16VgZE8sCDk8ah4tJRbDAiNKMY1Umaf3M6K18cgc25G63U47Cq/MyI0vHPWFLPJ&#43;xbpo1quTbf/Tf5zoLd8wy&#43;FQb4kfQn1JSrWVRCF82f2&#43;M461WC&#43;vomAnxdDqe7h&#43;y98oaziSPSin0hUBKRnC/qD7cUFQGMve1HtLqyVcPZA2E5TrbljtBIgp1KuY/kWlIDKWwz9CbAkBSG4DRgIIiHwzPlvUVW/MgDjCSWFDhSLWWBGhX866luUeUzA8jwQm&#43;axvoQA6RVsmHCQ2MdCqYH1ZYqwTRh&#43;dCmuOeKg5PlCoSnS7LspwXZgtu0j9uGHZMegm8bjB8WWRp7cgpE1MkctegiDTUkIVoaOL27bcaUWGZ5vP5vM6zCOHuxTOm43J1UDO3zNi&#43;6yPHbCHGa&#43;K62D6wwJHWXiU2ajeHi2nTG26iBxAuiAP4gvu10V5qEf8LWnZIGtVYjLl3UXFam9FBf7NnXQjWNmN9LHQX9daxvhITJ6aVtjhbinHcoYONNvfAih/o1uI6NmyMQ&#43;cSl3n2hFLjmoJM5ec&#43;8zt&#43;/fzqf3n8Bj2Wdf2R4fl9Xn6jUMz4xLg/EfU/curnx17E&#43;Kdef&#43;N/6N99X3Y/FV7/UDn&#43;Jff5x8cjMxSrgau8GqXuj4&#43;N59zIjmiB4FY2xClccGJXvXpueyhZOKeHHm6g7r1GrOJsVF2xd3/2P7gw&#43;DiNAlyOraau8nt4Dc9fcONVwtWA2hZCMEqCGUPgB/xLNPkEFACt3soV&#43;HN&#43;88DMDRAkyA9ACqekzHWItZVJeoZYrRREnxAzzA3yBGj1hgTfZuxkDSYhZ4Na3MZHk9siFgDvkkvOSuvrFvOGIbWgv/Qc9GMfT4mM2qOf8ajoro&#43;Tn2bNWCOmpXCKCDE8OS7A6a2jI3N&#43;8pIYS0Js39WkZIANa7KNk2dy46I&#43;vnl9ySRlcUlK1SLEVWdo3tJp3LalnatdqfyizwGtn0ueHOWQF1q4W0ttlfmW8POQImSbCF4hrvnh&#43;IjElboSS6EIs7tI&#43;YARDfabWZn9zgcYzffFXyJnmNq0Mag4AQ/YtVWwKf7X3CvmWr7D5UrDI8//5gEhm7JWjRQEA/avKILA80eAWFq0m8R5AVm&#43;evjM1w5f/Mvnb5ydcNZ&#43;VYzPzukXR/&#43;ZxzV6OuU/lvK3CKWc9jF8Lp1&#43;SY2uxK&#43;FT3Zi&#43;Qf9W3/17R8m87ysLbhgFpPOKbZGmgvzR6mu65oeWAEtkBFBP&#43;zgAMipQC&#43;ws9j/je&#43;MD6mJD/VTf6yBn4oeUyVnV1y&#43;lcuhEhD3u4tFAbLnwxPmBb2j2piOrUv0IXh/8&#43;KF1lXzT2zMHhAhIUbHQi2cheYYeGQmFrZyFWFDl5VzaRP4kpnLElxoKeylUS&#43;FPaOFuLCaxKU3pVb6L2ID262hi8h/Kl&#43;K7KuUYg6NaFGzf4l5sFZXuRYpaUNIaTkKNKLCZjKCiTtO0AaIRcOfqdSe25RcsXJrz0z8uwleriOTZzcnz01/tEB&#43;Z8WyiPNc02BS1m6e1m6ltwYjpLL6jcLRPCTe0PWgH6Jx30O/gQz0U&#43;DJFhvDRPp1vRAbrqRUvtw/bTTS1jdLcQyLvNVGt6pows78tqc/fVyWpZyXlJLN0thKGeIslgicHA2CDdAET84gvHP9MPTj2Dl34phfch0TOZTE4d5b3b4ZYhRsAOnBvUdIiHQp9vliM4gZ/&#43;YXf8de2O9Pr0dhQo7jHLRUv3T&#43;3nfzWZWyFK5BFKHWaTOL&#43;qsq/krhrmNjPk6iie&#43;heNb3fdd1C7eRXGtKol59fPPQqKnIZci6DclQokcxs1MsuHcuO9E1bB2OtEtTksPv/OPeewKi8E6bFEuFlHxUEh10xV0k3ZlhTO09TJHzNVzyqVm45Jm3WHJBAnKKkYvdnFWHT4aGI5gloPhD4IZbFHpjZZNZ2fQN6aLnuaoukE1FLpQNSgo4OHx4KqSsGoybGJpgaR7LTRqJ4VnYipZNFrfnWCXTmqSV6y6zX1MIo7SwkTA0/PBqnbsWlsh88OEpzJXl8olip4pPQ68sVDXIbLEWl9gaX/ScgBS4Klu5llz/ka0JoWoDZRAP0H5o&#43;nHc8SH053mapo6dfE2k13PGfv7FHeeKeD/xe2oNjzMdyYfcMkzIRKYr6HvpwWSBh6vqUfv3/qH2G7cKMM4zDmSVqpEXlLGmSYzjaDs6Tqc5eN9J4/jR0LVxQSI6evpLjtl7Kyx/DHJgW0uw1op7DFEzN1m0UMKcPVAVJApbRaNSbgDdmeeERoXA6aEfePLOz3zxn/tvvv7XhZJ/8vNf&#43;8fHD/76&#43;Vtmo6z/SBi&#43;4O3X08OU46h8JqBQnin54/Orj4v6n3fPz8Y1WkSjJ6EFIjbyedOx4cRw57pqUFjFje6CEWg39PNMDp&#43;bOkat9QKlNLR28IlAek/w8TbzGyZtKycNQhexQm5TqrwpfTkzsByiOJ9WX858fiSo9korlockLMA2W6nCUg2uciT2Xbeu63Q&#43;QhaEDjN4nlw1NVKlmNIyVzK3EIviXlwUSNDzAcKjGSoFn343MSVHK2HkAG0hmbnX13V9VaVkkx&#43;4KTyIHISIPsgQD1F1Wjs3WEsHLCxhefMwrevjxp5th39PYVf/sT9r53b7myd9byU9&#43;JUjjdJx4YcN08CZW&#43;UpUs1c&#43;znPE/1dCG07UPNSzrTTlZXkWsGwoTWcn2kknMqlynpRHkSWQTVwVEqvLPm3iQWdpgfuR1FSW6Gs4s3asalq9fnzw&#43;N6XKZ5PrPqmtzCs2EcdkpZvVO98t5PcSIn7EtJqiGsWr0LK5qrybiziaksXz6x9&#43;eTaE0gG5mQtUW0kiUrjehOoIieheh6mWVcI1QAjOkERYJlWefAlVjejbzXNRnrUOKGlQSFG7Q&#43;UYiYj2u2Nmju7l48XJ&#43;0dgnrJd6DXITRSUrBuZLAKZWlhGqMOiu4Jvl7v/hDf&#43;3XfmGZzkM3uE7Ic47TmhPXd6U47V4cdjfp8f4xhkchijIUxkV5n55&#43;oNUnSZQcEophUlCwMw63w2A5wjrO6zRNaeWqMuiTjCJL5JYpTnFm7iCIfC4WH4Q22nXJmCmXksLKWoKbMHil3K5kC8gu0G9ex9atpdbPi9le7UdSytA7FJ3RMdtoTMuyIEjj8peEttu6rl3vaoYjpeK9h254Kf3tHeAE/XTcAUJIKefj&#43;aLVpC9JpqpZxVQ1qArjgm5vbxt4g34fMsxPnzyhq&#43;KO4hjQ8B1FSqdUswvQAWyKcI/HR6WqJjB2JyI303WllGmajscjAbaUKksMEJphjAgZiJlQKBrERdXESFpLdm57lq3NG38deXvn3EPxZAi6asLXdV2DFymprsOh9d6XK&#43;aJGfZKqT2/JFnwmFcmwIIGwy2BlQnM9/vOl79SG1CVImTkfWQzEe7vmzeriVPs&#43;Lg1kGotWUC8P9BGfHx8lJucbdy6vlt55pr&#43;jQ2Df29VKGgS8hH1zPHC79CDloy/bm5uGjkxGuZjMrHkyc2zVlhqmk3kPznbQhjSuWHca60Tv8E&#43;fdpSbiHG0iRyoV7KlQK36dewCs38lbvnv/Z4/12Vd&#43;&#43;8O7Bgxu5weGo&#43;&#43;1PqyWeK&#43;6vq9SGaPGe126nirEZzf1Ch9Eo&#43;imzQeiFKo/TWvh3uedrfPqHr4foOeuPgb9fTRP7ZmIt8MuokDoiDDhTSn8MwmMOhngXGvz5F5lxMYl2l&#43;Gd/tkbYnz7A8NQ1FQRwz/suo&#43;orIGvE0FQ76PSklKbFswiDrCMFchYfv4TABRRe2mud5kv5YdNGZXJOTw&#43;P471NiJwO536/Ry4OSwDdILJY6YzKKmgnTGcjj/fq41ct/gGYLPBsaUsmtxcnM7rdrsZ7yK&#43;m2lFoPveeEMImFjbk/nHDYjSitwDJdOLO5A&#43;RCxVMQszb48yNJda0RFjro5FSuttda/aoqku8zpjV0LgljaNO8ba1jhsVzCaRV3totg2Ec1O7TrivACHJlgCxoMe0DlUfc/Iej/j5zU37TFS5yXuktL&#43;9bQ39dZOwMT07cfHAUJXSG0E1JSlk13W73W4YhkqPWxdEyCAbNoM7o47NlWHwhBExeisvdXLR0L2k&#43;&#43;LchNxcS62Hu3JpYNicEzme06k1XQjGTRQQhbB/vfxANzwz7jOmE1IbpT5rdlNOr/28V0aV/E1/nlP4idJ9Yz09EKSTWmlj5Z00X/bhF03&#43;u4qLC36t6KnxwBCvmr5uNojU8cmBUvRFKRFV7tq0WNRGyWzFTnqaUIypXRkXpRH54g/&#43;6WYmrzmGMAwRj5DjYWuZyFaqD2xLLMtFYbBwE7livM5SDMvt7b7lNliWvnaBDPvDRZLyKl9izVCJv5uuXE2BQKkkpksYhg7EAWSPmiHlUSm0QAeWBUXqDxERNJYwFKNxpFGKiCGI87kebAw0sRbQNwyOwH&#43;g3Yrtu9EDsxwGx&#43;RQ6bkuvXA0uC4V6hijebALEkIde3LH&#43;XbJggyB2yGXXHtxaLkY5XKqoZumqVy9Ls2Gnhu7uW/GGXtNt2iGAycV5s9w9lKoSsDgCgKH233X5JNSFgufKHLUb940VrbB02RzOZ8ntNM00hi0QV&#43;X9SIVFK4YoFXJMSIDKbpOcoJ6t3mYlrbBRsL61KYLKVr7pHv3xUXhZDNnbaMCCVaVT7Zb885cpHNacUvrt957D7/Y3BJtx9W/cwSRg4VQSumE/P2T&#43;47NP2/W97z8dpyTFD&#43;ihp/Uu7/i37xUGWxk7/1ni/lXsvslU/7&#43;yN1mY59iquJ&#43;hmVPWTBwmdaGNEG/QVH&#43;Zre/ZDfKhf8ntaCI5nSe57nk7Lpuv9&#43;P4&#43;j6rnZ0b3ojcE5S/NTPXXxRqzXljfAETi9U2jgjb5muW8KVIkHi4qp1XC4ywjk7DtZan1NcVzGdRL2yqmOMYga2b6M91RklKQkmdSDqi1VaQAHQ0nNiLjR8CSY2ucrYZA4ActQMxYEg1CY6w7/O17yjezHMX0eHSm37gtTDsqamacQmrutHOgbMiHZIgfO6Pbx5zZU6Bro&#43;pnWtQHqoIl0XWhVenRPLWsVZay2dLUWIqL5AYwzC9E1dzGyaZk2pcB47sc2gkJuiGkEyrhLHksSm/Fzr1X5lk2SqZ6C/O2VNAU/I2aEfbNdDlZLiJYZnx&#43;PRn8/CM68OZWLU4XMB0iELCAjKArdbFSBeImH2cpCPral1TgEq7aAjba0tlmW2mOr4&#43;PjY6qKKy4GaP2kty/XAhLak4&#43;3NdDqLGLqbm3ffffcJU4vXdT1/58MmYFI9xFYWbbTc60kgt7uR/izqK7L/e&#43;U0avvTb9z3uvz9z93&#43;&#43;Dc&#43;WY34hbfd50/xq6f00MnAUuV83L1L&#43;Z3s/5Esf8tsmYumtWYuHTsQc4dWWfTh0pfeGnisldyxVFK8qG1vshj4rRDCAGkn3s8&#43;I1XsRQjy&#43;b/x5y46zFcMpLQZMCSTSylV1OL4yOCnND0&#43;Jenrz9wCsXI7nepc13WCgdBBXvSBKtNgk0FplOOWZM85292BDDxGtOBIs5eAZDkyjXVaDP/WdLwXTbK8iMZoQTBm&#43;UqACABsPlpPLQqtdVHwclh9FocEdc7egpysKXg7TqfTKaJ4w1bWvf0C6ocFSZR1JXBL0JpMWL8bh2GA8iM85IcffeTXFd1CbbYQLV9MF/&#43;JwJJ5OaCp6KuOSIQMp7G7VOavXPSz58/pqSkBrSw6b5jNE0MpBZ2rKzpXgb0QvUu4xwF4gSIu9jBVIL4IbKO2Sqi9q01mgJ4pR2VoO60zYviaX716xXeuGnEavOXjh6&#43;EMeBUlXQ1KWIYeCYNeWkHPg0LlIUdBmxU4dXGI3jz5s00TXmakL5iqQkvlkXKrtXwK5LnqL5ygeQmqbO1Z1YxQyn/&#43;Ntf&#43;eXz/TfWx3/LfuZX4vHj5fFH5c1fCx&#43;9MuUL0TzJ8pfjKZb8EzfvfN2V0nfvavulmP5&#43;iffLWcwL&#43;Hm1ccVuqtE5CyYqWkYr9amxkULMrwyPXOo7DmQ4YfN4XJYlnaeqOrjVXMTxWCnG6GDfTIa0P/sfNa7cBZkIcfvk7rqftqn&#43;D/O5Rmu0B7iPjFNWZMmHwex3rNBfQgin&#43;SzO55EbnWGhyzXTuIjWaQyPh8RVrGOsLDotuXXRcb/ljG0NmS9sFKXUE2VAzL2M/2B4Xwn0WjUaPVQRhr6HVWuNgYqrLgOXZNApmtDghg03guPNfOxYmjBaDkvViHBOK8PtZmQypvM9Otc55rkEbR0PBxOs/NS0I&#43;nTbroqULj5LlDGLOIlmKSNB8ZCMAOoo61cgUw7SCOQpE9aZgx/idGwRBFAi&#43;Q&#43;rYD2xt5xlkEZZyVkX9GfcHpTYy2yO6pc9X41vaKqA8gWub/ZX1NQG2qQLJoPYkNrM1RK9c&#43;f09k0dPEnidA9ie2h90ynHRNj&#43;MCh&#43;HxutJzqNvnAK2s6Fnbz3h9PJ0EhMW13NafGSFNXjDQQJ5rMW0NGctchafq13We&#43;LG/&#43;x&#43;Ov/FH7A99cXz8r9pfz/TfVPLhuEOqzx7j36f1evDVPn4/x/7jZn7TeaXVjzcOBXM6aotKboDzngxbWkJPLjHYLFFwJaqW88mlC2RIC9FWcMKXB58YpFCwAFOc1hbA7HNAk23h&#43;QIKm9WH/phj44&#43;98p0bVZeMJGKOM2e12TWUSBzjydly40C8yPa0t8U/h5vTyJSNwJmfHOnmALaSpp3dZUGMsxkSku0IQ0xSECEYvEOgBdgKhomn58uVx9r76rpJyG&#43;OCXpBGioRZKqU8PjxUEvkGZTPzV0&#43;nszDGmipVxWiFbT8PsKhs21RSTCsn2NJhFEKYoSNPm&#43;WyLHFaUkpPv/zlS6eEqmp&#43;1toqy3aaOBlLMRsMROGanma2mYFy1cS0/rk2iDdkgUzBmlfyJKqGha3vwi8Li&#43;n1hH2cgTZVDOGpGriGnJGhQEaMjv08C63trj/s91CxmDkM7l68uIilQGWKvet6nhAVo2mkJVfO5/O19W&#43;GFSRcwWQbw7nWdV2L90cknwbXHQ7D05v9fi&#43;5XeTVq1f0LGbvz&#43;dl4igGWX2/XGSbyqYlyq2ak3Pd0GtO&#43;EVr8azlMuMOxQYSeViXaVQTfqiuicUGlfGkTjpbqZ&#43;PB5XUZ7vbXw1vvmlWE&#43;XzpehMEfW7QX7T&#43;F&#43;35p9Zlq9M0z96/vyQ44/ff/Laqu8&#43;f75/chtjXDhTfhk5xFXYpsEaQ8DKxHkWvD9F4WIS2GaceJvXVDu6t4yPVdrtdt57ZKQJUW7d2iklc5N5oddMZ5ILEop7NayljSswLnHonbVelrCGx5f3aIwiG8AIsXAMY5QRqcjJKyltTaNoKc3y3mdZScYpzWzbvu8sPbDjm4fWCVnbTdgfLjJ3XT9aspfziV55XnNKRhsyQNxzioNhtDPa2FvySFXo1LPm1ryGECx7JLNJbNc8LcXqUrjOKXp&#43;FpQ6vv7C2kWrpIcM9UYeRukSO&#43;i8hvM8h2WG1pzqNKLfqNXK0FDKrqS0zjH9&#43;stLj3G&#43;sCpA/b&#43;epMu&#43;Nqz3R&#43;7g1VzcTEgWGGN2bqQnIosbHKYWZrQEJcwu4NI3xtAwfnXqlh4wBpQWCvn0unrlT/f37RoaI0qUouEyw/H0eL6IPwtxRLmuku&#43;3JlBu1yrLSkiEhdRLKaO2XdfFdWq0RxDNkpQpi5yqBEwWFLBVFFOKOLOHP4n15ffXko&#43;0/mjqLhfTnGp3Dj2XEK8LnC3sIo&#43;6zvnhnNjtu409di&#43;zsqowfjHOdSyCF2Psbg570Js4X0h&#43;C&#43;1Qm3jsQ5lf6vuP02S6WeQwF//T5clvDPHzi/onY9RLIQdxY1bn3vhDuDXv7rq3Pjn/4ydv//A3v7u&#43;Ov6TwXjvC&#43;ty9AxD7hhxFi4Hoq0lVKUx2jBOyxgpAtOYHlyyycpqG3gcqWbBDDT/AFXdf/JJUCpZ57UKPNIJlWHz5qOP0LfBnpb3M8Mkx5I6oRRu8vJKqcCo6JZpmb5wLqt2k/Ka7kZxUW8tl5T33c4LccZkFrjNwr1U&#43;8NVI36pikRKycFNx&#43;P9yr27tfOJLFNkD4MmGHQjo7vIw/d6pNaQjRRQ2b7Eumy6UCd7vZLHsJw5VxCUhCALwQsz8OiKwNMSHx8p2i87ijkx2bLNncG4R9V1znRscqd1XXXMjf/wm5pmMfztekRLC1WweojZ3DbYpU21VVdJrID5ibOn/wVKtXorApCDZo2kuYmnFj63L7jbrE6IVrKZFbTILtzEglGgQArvvvtezom7M5LnsTOCzcTxdPJchIPeewusKjW/an0U6DSIlIabG7qoSlorELKhu&#43;PIvNLR&#43;TmiGg&#43;lsbjwCMtphYh/LkVqE6GCyNhNbTKmoWlEQ79pC&#43;uE03kTMgkbIyXGeOTs&#43;oUR1XRRUOyM6aGU7xr7Q7fP3cE9jeqZmP92uP9sHt6V&#43;79flre0M0bs9v1xmv7Gs&#43;zz&#43;e2XJ7OkXyviS8584XH&#43;epRB0o5i5MsqmXyazkcy0EjaGeWaZtv&#43;cFi9j5x6RJtn4VB0ErHSYIW4kH&#43;Vun3xwhgzsgRS8P58OoPcaqTuMKgdeb&#43;GpWPVdUGDQy48dlxoFzMTBXlSdVX/2oRLAK2rgGMj2b96vNTxnBPGgDapksxZiqzBQKy8Qq3nmSlZdDvWdgN6LHMIAxMYGEcq2l/IPQihn&#43;x5zC4GQF4oaYbnJ62RfPJxXcSZhRFTEne3Qsq1sPW1zvYa3uP&#43;/hV7m63&#43;wdxsruN1gsfEwsUwsSQrldIyZedDx02IPqmcLa9L3o/XxdsMZaacl/vaBSac68YdsJAx5nw8gR7eCj8I88/LXMhH6IyZUqIeeoc0Ng&#43;vzmwyYKcPh1HSeootWpYiyVLEK3&#43;&#43;VthrHGAwZ2lX8bArzzJ9JcbenclYcJgrDDkpxfKuT56&#43;Redcsg55Ud775XRelkXqS7af0KCOmckk86t7rFiTvKm5dw5JnO26YbBdV0qePYWESINJbe1ohvEAuK6UOot4rbLATLi8lDKOT5uQQGWVcF7KnbJIYqtULV6ukIiS3FJbmyJNp3RVGspkJcoPP3vy29969u6wTzF&#43;cJr&#43;5v2re6N/W//kR/VwDmE6rlJLa/vd9x9NnEqKt7l8SR3eLvp70/yB6/ZBZj8JrXKhEG&#43;NtPNXNIrYPgkRlyhKgIA1FE5O5xV&#43;S1vr2CwhsixvTjjRGdMVt8P88OFZaP0AVl&#43;IaZ4Fq5dJ9bU/wdQIhXbntkxgGmfJMpy58NRCspT7YtC9wfGDaHPonzx/1vo521yCGOP9fEKyGolEIcTC6ruBk2zoNL6MtCWIq1nJiZn8mkKX&#43;Twt87zpM6aqNthYRKg2QEFXXG0UbSRDEYp2NmZ15q4jgqbTmmJUATkRssfuvbdaH0zlPHFXbzxOBLfWCBGWSgjJeXz&#43;lGlBFO93omodEigZ7TXXv8WHPZJnaFWpsrLQee4vMESrq5nDGn71UlNFCHCMF8KAlpeSVetkQNoCVVlCOv1FCqfJ4tL3dlfsXHkl2ScrmCaDy6Mqoc/M/bdKspQ3a1mFefHeS44MQCCRsAjOXjfGIOXbum0yJB8sBaLgFYUUIUNTcxPokeKnyQTetQ7Z2/orsLAr8s9XnYyQWLld9XU6tjEawORr&#43;vINKHV8sJ9a87PvPRfF/MKbh186T0WI4/n0rz5/Z8zq762n34jLV7L5raJnLh3qBRxRx/UfvugnK3ZLeH&#43;hzzfVOGa0TNDn70ZMGiEIXTZmOHLUaOs1RnPCL/M2GExfJRDYgIpNwF20cS10&#43;8zk4yKGND/5J666f9Ql/imijjKDEhUT39Bw35Tm0axX4&#43;GrPCoE8WSmxRuHUeuLoAVTg&#43;aFVv9q6UHkqPLl&#43;dL3WC5ZXHE1v4e2tbUKzQldTdnXanD73Toz6uq3sNFdTz9ame&#43;tTBsFclonxXXdWpJlnRA6ctMiWC9aKTVwnyEUHo6RVZR4JJrkgpNjwz&#43;XVVxNV73UgeOlrawhP/pvWq/ThMJUjSizG0FiqVpCW/&#43;tlv1vmn0Bz9z3vdoIbddjLM86fkqYthk4qIvli/JWFaM/e9Em9MID8J8dl6kaFQGSa1rrxI37KzfQYewl6j1NlqwVwFB2cocdshK00Y1m3uK&#43;7/sqjM4v1AhQv0VbIhSRINMx8AsqbuWfeq2y1ikqL3VdCwaLY&#43;ujGFYXk&#43;&#43;9zoiSPziYU5avQqp7puu05aFTmNse02/xpUtZTCGVEuiLykudX8uMbhDVj7mN48VTzhgBUwfNYzAKBgmklHa73YX4WMFaav1SievJYEMkdhj9ftc0ksHh0ygy3v6e/7BxQbjzTUDJ4dlbbxtjMEEXtpMdVVqm02USwtU03ca1qHyMTSl/neZLJRAy4hDXljVOE8zxajbbYmoOCtHpIr8aOIMn2JdWnhZfwzH5TS6rdre2QR5oZkDESF/BWfxeUfiUzjwomRUtwGLVe27YMGqbJ5bQXfze87c4yRd8CHJFwzS9393ugVAC00tyziMLlMdDJ/6pEZWYhdO8cb563bihuWs6rjGFTYQF6pBo&#43;70Ew/fQeb5oiRT&#43;TCRmasn9eoMO6iL3cSVTjpmWg&#43;scn5BWWnOqb&#43;WoOmufNcCmdaFnnfKK4ZIsh8RupCbDW&#43;Ie/g3rX2lSsRYLC8hc21SnLCnqsMxXW7d2RaApzdrISqluHFBDmuf5fD5n1ppTxuTzGSwINHJncJ5ToiAI&#43;RSQeclMEy7YDUMrboFKhXp7G9HeXkJdkuqJCdWtXVkI8bYbGm6/nulRCouusaszoN8JTagN42krZlRtEvJ6Ook2OF5p10PgQVZFaLiAKk5IV3J8eCO3HmwH2QDok938rj9TSlkQTqhSlZC5YY0sFhORDSpN3EbfH0ZcECOTjYwlxO5wUwe9st5NhiCDUjf9Dr04bUgUt0RFw/299AlKV/vEFxoeT&#43;gNbPkJ1HIH1kCKorTBKDX57tOF8EQX7wDhIOPqI&#43;tuV4Fv8Gl50iwzq6BLCAE00Vs4CzLP8E4CutBFGCu4JD0Ynrt52HVdpw4D5qmfTqfT/QMhusCB8sMRPEcMpGj0g5a4up78Rqux&#43;jYdco2hzrwqzIHrB7eNpW4DnRNnpFt&#43;Tl0xhMHf96xNkTYu97jfXeYzc7sluq/1VeulwvAqrhK/zGudsGGt6h1mC/HUolp3qSTQEMTEQ3MeH1jDqVO73cjj5oZhMFxYjpyAmCaKgMI8Iwdhl8sU8lSyD2HBKJOtm6cFR0ixJC0aPK78ItxajIJrRMNYswnYM5br7WBxe/72HClKNzxkHPukUncYWoP3hjDwejTP7FfRuInpIqy/O02t7dSD1sLH1fV8sJkpoGAOCj3Tx&#43;dWtIYKRo6gnUhMvSLfsFY4TfFL2p1CM/FpQ6lKqZENEOq1AYMKQFwZ/8U/zdEsfyO3yImBLijjhhmKWC6sCx6cNcdFQKqDZzRfJujl3Pf9OI7QjlmWBRX8NK&#43;0vvYyRpQTusHwjAJymLYOK0UOzNT2UrIcVTUAuhY8PiuwFlSNAPnL99pVC7olaXBQ2ry8BkSBMgaeCdALbgNYmKXGyfc5R3IdrLcsQgohZBZYz7bUpvnISsvcVi6ck4eRRyKDm82mgYXmd90oP/1q/qn101xo5FK62vTO7ewcWeEfpNFD35vONQID2FReyXKt7dqgeAg8l9SAsnSFAnKDtSJzP9h5IjjAMJgH4muQUkGAWfZdZRQ5JzFIEKFKydzGONGh1UYPQ8fTnvQyV62vNsZNiE/1DwNPbpztp4u8TIGqbAXWzwHJUdY8U1P88Fb61QcuYahN4DJv5eyribPbd2kWMMCE&#43;82/ia7rtUWcSV6de85Zb8Lf7PbgkMPvyU2eCeL7FfWE2GJU93hC2MX6kmxtOHsf6/QGzReG4Xv06/MTVpXhyYzDbmzbAEM5W2iA6Xnruu4/fmxJdc8sOtx1VeSQtUI0sKYSfcvzP/QfAyZxLy5LYaElnS9R0p6MUPFL6DSyssKzy&#43;BpCn0GnuZWkYZWLS9VQkRjZFsgWgm/zTWG3bVW9r1QssQ4CHOZn8Di7KbnNsXd0AZqghUws4jh8GZpxM863rLjzcrzr5Q16M5Fs04V9USGmctmBNHJZwzd7d4YE0uepimeFyllz&#43;Onl729Vm8i/4NURG9112Ut6Rgv25zblMSZYirTdSMLNTfSi19XTJutUsNbhWOJYTP9VQIemymWjH0M84fJRt77Uwh4NwAhl5Rlk8W9DHzEcUIiBDI3mH/HTQg5546JNGCD4V/AA787621KLAULbP7IpUB1EZeEETMID84HvTkJVamTW48RXRIHBVLKrq/Jhcc3D20AJwTKLfv2wZk5ZqkpxB2Zz7d4n5apD3JaPXrcrxkj16W4LbdMHtuOfZvYDMUvhHI9D6aFjAFIJpAiLvNSx8fgT&#43;Y&#43;QEkL1YELywDDPnfM7pZIHGrddcP&#43;0Pf9Cg4fB31sMZ1hWfZlmcDHbleOYEfxNm7b8lLcijO56L7XLAvnNs6JZB8Zy2WSHgQepPnan6kcWmMyt8gF2DCjrXO97sgGsN6yYOGSm2c8o4ij4iryxEXF5VNZQdmOdzdsE8pDEM4eDoeRh2Kezmey7lvGkqLE4MkznFfMyKXvtYYg6250zj3O55bNq7V3fo/&#43;6LFOk7hU9jZ5zmFQQ4/raWMQpeUSIjLGoF7ysT&#43;8eEomjdsD05lcs1jZW4qVYY&#43;jrc8HXnCOJnU8wEXQXteZOcOJUNkuymWhc16jo5zlVoi&#43;xs8tO&#43;qgBAL&#43;eUHxY8tIwxvww6vjTjAFsj3yzd8RAnp4IJ/JMi5NvotJC2tTnIZTTp5Qa26KKBxzim1Q8rOzxlkk58CjLtHFlT6ttgspJTJMQ4GYpuXB89z4VoNM6FHBdQzjUKfgcqI0hHA&#43;n&#43;dlwYYxpfz3P/r0Wyf/t17N//urpTYGxPjTz&#43;Tv3om/cTJ/Y&#43;6KrkIxhMbXVex2n8quQ16C3hCaphe&#43;S27jTjAOtg5V2TL/jlVNa7SJ6YHsADSTtzBtELORwUuLgplkVVDJXclOidpQ2cARVwWrFnoRLSjAMa7jNK8429jVqldNqLwpRkLaEd1IrQ2j1Mknf&#43;TP0znMhJIFL3HKseKxvteW7FadRif4glbfSuqOMYBh43c6n9GOjHQRRGS01vN5QmBcdRUb2WM3CrA7Zn6Kjqdyad0JlokLqN0n0WTK33pRu2qbb&#43;FtNETbeM7IhwM2V37V1kPXVDUVx5Boqq6T5o2yxjysk2HpH62URR8Hz/gbONupQlq3iemYc&#43;NudjAoOWfD6El4CmHd3QGtlx1TcFoD&#43;hkUTkYrHVtWPJgjFC1Uo01vOfOFK2clX&#43;QB0OBS0H&#43;f6nbZmis7vs4qV4R2MyTMTOWLXoAlAkjQZjZP3lDrw&#43;moMAsXEa/3OVS5rEplRZS4pXy6KaCVDymxUgprhSxoHqhOpmQ&#43;VFwgfHZbU26ExtfW/fa//sG7mNK/&#43;w/l94MW1nRdtx&#43;HP3f3nWHK3y/uL73pfvXRC2PG29u7u7vdbvfhhx&#43;iZb9SD7ZcTO3LreHuNjOINTeb8J3YZjtx2jq0qUWY9iiZXnI4HOAYyMR7SFtzGWx0SDDwcJOx73vonIsawqlLpZ1f&#43;/2e4AC5CtpPQAEoNQFRalWrk2DM5uMEJoV1bj&#43;OKC607AnSZtcRu6ktfujmRSwqbHKucGIjXw8UxgHoe8RvlxEkjLiaVyF8ezqW1mUiVRXd52kMchz3z5455z75&#43;COeBDsI50Sb8Q31QGNk1&#43;lxTEq06YTY/WoYrgsV5A2&#43;f48HSVciLqF/Yf5q/eRSmN/HX3F3yzVVNgErz2VlJC2e3MRlqYAGDZIhiRBPr18j9aW4NYy5zWQXz8mDhds512mosNFmPcYVcgqn47HKXHCpzLIiREObFwQIpYQtedvoHOruFhMz03ZHUEfpw6W1sDUVNOJXo00b9kJa60lfhkuif7j20/mQtwcGWBNCwDzTim/lpcGoHnsMTN/QMqj5Jq9Q2CIDzYPUgMs2HW6NOjwMulLqTVhr4s05oU0V7qbfCjHl73snYhDrsk7T7xyOTzt1H/r/7Ff9yWS521lj3k7zr3/vXGcdbpAAcpjYD2PnkEZFW0ubHVk4lVW3jbgUij0npSDdCkUuqA7d39&#43;3lhv4cLmRzzDuNCoCpiklzfthXhfutJPI57du5CN37&#43;UQL0K8qA7UMdzi4o2cFdZ21ibEyet6j2z/1TauzkxdNMmk&#43;N1/tnbPoHGJdlKHyJNzgKz5yAKJmbOg3WliageGUCcM9VRK9Xy00Nm4bMM&#43;SyldFNaYjodoRZ5oOp/PHEs7ZAsKODSwEVrLmGEF4VENKwx1Xffxhx&#43;KizpuudQwq8LGNgVHa4I3aIHAJAc6PwbZktorm1miaRtvRcbZ2mNc20lARVcv5Lpvnj&#43;FimLjiiP1AmuNTQlusI70&#43;OdRj&#43;O42&#43;0xROp8Pp1Op2VZ1KZih00QQQ8WNcUK7wdFrlBp91luZaS0jWynwL50G6lZQF1sU&#43;QI2rluNw59L53JKQP6RskhKE&#43;&#43;t5a8xzxTKN8wdjuKVbkGEwAhElAuya0CdcVtyFtrGnljr&#43;Yt1dS3qM3kPI5IQYFkQ43vqVFxdQMZYND9Ukp/8cnfTqX869/&#43;UTC9Ry3&#43;yxff2pXwX3Vf&#43;lbuCoORn0jnn1k&#43;/D/7t/7Sky89sFRASyW0tk3zax9el&#43;uqtAiP3hZX4syNZnPjem6/Ye1omVtJ6Qe&#43;&#43;IVlWebj6Xg8hhNPJ8J4fWFaD3YCFTfT89qNI9o81nUN84QBK3QuVh7Ew4kNzIKACYRBqRP3mNvveGxduduhVdN7P5&#43;naZrQOe/6rnldzDcEA888&#43;&#43;pXDRvmNnEPpKnXjw&#43;WJ9NjZDbrCUakl1GiAOcWphX9ujlna5Rz3aEbW/&#43;t9XlZFs9hIfdI2P3bb3ddr1l3f10XQFz2ZgQY8nlZ1&#43;VxOtM5zyl1ne07rc2XvvJboH6&#43;LDNmL3Bnv9wp26IX6Qy5Qwbwj&#43;cjbDC6UpG0xFAsNDywqC1zbmWZCXKrSvbcwC3O86uPP24kU5NFg6Z3d3fw9hu5KnbMUjqfTufzmcwNBhp1XcfiAY6O0DBwMQCjzLbUdGDvWw8wbTVG3afpZNjds9Z03MbBxS4aFAG4F141lcmBEz&#43;aC3JJUcyi&#43;f2609zhbBCCIvlJnvD&#43;HkYhM&#43;xqOx68mnoeuM8sQXuZY&#43;/C0zCa&#43;6Kd0GuWgDGIfqHXjeONmYwUR8SYvRcxFCE&#43;8hxkF/GT5sNel7&#43;zvgtlr3gghLqsa991w9D/3P57Lvm/In8we/8FFaSyRsnfN9Gz&#43;LHlzf/7&#43;MH/pm5wEYKeQglbUmBYfSu/V1vT2FpMFsqbAj4OPAaLJ2YlLG0YmlJf//mfr90BSkkeUj&#43;4zlob1oQcFVut0Op5mERB8b/3InjucZNZKebmw&#43;/kTYK/wPldaMgY48rTBM8vk3Zu4NVu6wlNuFb5r9Oz2UEaMQ6hFM&#43;ooyw&#43;xAj5Zva3/F2rX&#43;bCHRVkYm&#43;7XoRAl5JLgNh6lMYUYWwUMoS4pJzjCjIMmeSHBY&#43;Tp/IpvwR/Xs/qNL15gy5Q45yiXwwP8ZUoZXD9sixlmbnQp0WWJ3FcTstL/71PtQFuTJR7NV80kNRGAyxF7vcFxXrasJsilDExpFKk0ta63uw1Ih/6Ue8QGhSeNhjDBAEC8WQQUiZR08QtS/zxeqqowbAy5kB&#43;Xzk3mhFHBYkcnnaffUrTspgYDTe7obEOG0uWK1o/ohJ&#43;MLZzUmpRpNHWdX2bSPR4PnEMX1jhnDOiFILIh3ASUQovkWKRZM606vXhlDgOn5pGFxK2X/zCl9H41spa7FfV/PBwCcSbBih9na1i9C3pxcd4fHUZtg5lb0gdDtwHjmQSDAp6Xz/hErwu4v9Oz/7r4e86nf5m&#43;owqQpw&#43;oW0c83k5/vD8nd9v3//vPnnxF9&#43;czZrRtPIHnrzqbz6ak/xPX/7g&#43;&#43;sbHV81lN6I9JzNthAkALVLbhi6DvCXn5q9TsfgzakO/hSClXxLNtvgRSk1LUCQYVpjXD3jWPS313CoXDLYdW5mrIvHbHwhxLTTKO&#43;R600K6bQKztsEZlnJ25yk7JMxSyXJqqyN4C68YbyjDWjQgkrXZjlcMp98&#43;KHAPHiM51QqcpcvRKUjmnUl6zCNnTDm4fF41SfET5Fb4TKE0THRF0Oxof&#43;QDWxkIqyIdD/5&#43;HEYMMwK82Z7djUE5Hzsui7e3jjnzEB26DhP8zS98957SMZgfOk0z35eONnGtF5WTuv2dHjA1uq6bub3YNsRpGE5mMykSGVYrwPKiUq0sV1VhIUf/DAMfd9/aAOLtvMvZbyHtmB/ewsvSrsn5mmepxNFF0KLCZ2DCJa4T11wbcVL6bc5mk00r8QSpRSr9G1gMj&#43;7&#43;Ziha9n1fT8ODeIG6GPn4jXT4Bu9gYduURyFbPO6ljnmlO4fatKRrexFffL4wQeiidrTLzo1DD0r0BHs5AFxoOzx5lM1c8vPPVeFp8SPI9fOVcIFGlJHYJ6lmKCURhEL7SLBU39lUipwEPR/Pd/92zdf//b9m//nfjjtTkX8f1z9CZSmV3kfiN/1Xb69lq7eu6WWhPYNLQjJCITAsU2CbbD/xMYhJo6dcPJPyJwckkzsmdiJ7YRkzASYhCQ248RhAs4YBwy2AQmQ2AUCtCGBtt67q7u2b32Xu865z3Pftwq&#43;w&#43;nTlKqr3uXe&#43;2y/hS7W15eE&#43;YcnLvzL0yvvWBkfXirff2nfXLtjfPzT/TO14r934eALNeXc7RX9Qyen2Pa35kf47S529fluQ3SP2lHGktZyEa8dyDVUgBC8VdqbELm4EAmUlgs4nVEkhArImOpK1zUDpwiOos3YEYfSYMYMaTJ256wDvzEwbRAOtbsQ995i4GGkb4AJjFJGeJ3o9YVMJnTtpJEwe2n9R5QfGrgK9VIyyUGbG3vu0EB2oxgDwaQQ0hLlzCy&#43;eAKVWyeFkUzqfRIWXFgiVulKYXUqODhWwqpiwitV1hUBWfbwEpLGQ0CXpJiG39vtDvavXZ5OsHdHwymb9tf25XuI2jjfqzamU6WwZsNRcuzuwG6RMul0OuWiBDYdldIV3ITo0cs7nQ5vQALhleS1gOhdUzq0iBhzLKJnCHPEal0VC/RGIsB7o5YTwJyxcOElqRShnPAkrGz0&#43;28HbI1ledw8KYuVvNXYVabQvTdGERbSelMX5WSqlMKaHFss6BXqqlJBxihYKCSAt18ibAtUK6HZls5aFRHPKEkFalD7dKAhk2rBJLRWrqyKqmgNzQRyEIkFyJBN01R2w89U0GZF07aFArQ2mJg5Slxj/tZOqHxr&#43;ALbgy50&#43;I00HLI/EPnr/fd/emi&#43;Sw84tWmckytr7xIn37t9/VOkS8eTd&#43;fbi&#43;HFP9VHfndwul/5f1Vc8VS6SqR3hOjoXIV9BEFSgcotHQ4d5mYqgYy0CPbYxX6HohOVvdxkZrxXKGcvw9eRvCGlBD1g6oTgIFfsAcjEtQFzLj&#43;31iPlA8SJQiWCNqLaKOxg8VBPjlaPQjHiy6oyvjbhHWmvlBcSLgkIdJ4T03ABAAmHYC7u49DL43qO/Orwp21Qa9EKwEGDxztPW5BXXcFTCGVYZ7SyurraHQ3SNDNbrizLYjpbLBYOWvAIQlBahwwQKBJowVxDE6VzYD/m&#43;kIIB6MdPDlySAttUc3ncwfKfSgio3ui9bPFbBMToTi8BieBEOvmUStvaWWl1eLA4U2CzuswvuINHbRWCo&#43;nPM/BYBPkPEvQYt8icylJnofyD3kqMXsOAQX7Aj8kFYZlFYhgqOgXEX53p9NJ03Qy3WFJkmYdKSX3RGntdBTpx0aO4JyBW1KsfwiI&#43;8HMGefS4dq0JmmKvR98r4i/CfcFFTJ2HFirNUdpBdjg3TMIJMpa3Ag2SxTwnLUFRaiqQuRpAkAiuOuQ&#43;q6AIge6wqPitG4MB1BbC&#43;np2AEGgEGWAWKsbcKh8H0EqKI6G&#43;LAIOFP5&#43;EeTRlS3JerxAp7kQ1ace814T7Ojp1Ph0tSvsCGGxtn9q32/k35tDP&#43;d&#43;idj6ernYwmsPEWi0VLrsAem1HKeF/rkjSFKU2iVapvzcQwj4ay3sG/XQG53Br1IGCJIH1RjcfwPJOwqCQomQAGVeMwCT2rsFmADVesE2F4C11RmUEv6fkL68AEZig/nmUZgwZenqSgoVjjCm&#43;xwGm/g5Hfhq870pCncdiMh2DjngW1gPjx395N6fdYVDJcChTOM4S8OQPy9iymao1QIKYrvV4PBCcFKgAiYjMsPpRBleFhYHJrd9k4ntbGhyzd4KkTfu9uTytHJb442cH5tdkdZEfPHmrIXlRDM&#43;4CKpXHRebiABnORbyeNBFZxgHri2JuM9AljqUggu9h1MQbNHK7h3HbqMUCnRNwptX&#43;12I&#43;w4MDZAZ02HtCtpqpEcVF9nTOF66VUkBMVaPx3/gGE8IBs5fBUTkbJbE99sOunKKxI2vFa2LnplGlRBCLaOw/V/athtcEDg8Exy2wGnETeizJNJIQPIr&#43;kVZ7sVEPDBtSo&#43;GfRPFahHxijoMHN3LRduGKuAHi4qM/lZ36PL/W8uQ/2D&#43;xnrzr4C&#43;HlZYwLsSQlG8&#43;&#43;&#43;UHLnz/Gbn/vyS3/vX6ScXkU&#43;LgY8lxBPSzPRQ3lLaHxQGccQQdYqcKriHECRAViEOdViGk22iPIO&#43;qfS/Y4PDI5fS73DiRx2yipX&#43;yRsp/10Awru/w90GXgsxq24XG0VQxm3NIxPGZ77JgayNAMDg8PQv4yjJWmu2uQS4X5pWi0&#43;mIpgHgG/Vm5HBCex10m9NwcqCrkEfjMmOshiEqYxQmybPptN2Xu2AUGifpqEflIJLEIch0Sjj3FEp8AJ0JWBESrHp1VemynDZ9Hdw2mOq3/cNIEoANhkVGC6x1znVAAaMdWeP0j1KaZR00dA4FvgUJnsU8UsCaQa2gDLQsw9Kty2K33G9PB0K6oxE&#43;K1XXDHNauNrVlZWWTYUj&#43;wyckxFQaWgcxyulnAp1Zgo&#43;sQyULjAHMVG9jiN6jHMu6hA5GdiRqFRYJLhB2MSzrEWM4M3mee4ARhLWsOugJjaQkJVucHLFpXWSpizL8QDSWtdl5W1DpoN3Jzw&#43;urAZOp0Oqu&#43;ihyDGnPBedkpjTKlq9GREPnCSJAuYi4ZkKklo4/zYKjPi3y0jXyQ3Gdg2kJNTs7VFpDyUVA&#43;Wz98xeem5wfEPHX7z8&#43;mBuq4Pn//iATf9Tr7mwLOGAk01IsyalQ16ASkWCxFP7xyD&#43;uHYsWMYRFsAqYBCdd5n0b8axKHabAWHJgQUv10RgiRHxNtChdoESY6QfGI2hyi6ugaNcVilHt1YVe2N0cB2Nq2dt/ciDzkaklWMdy0MeXVpCWgYQIREkyOcpe&#43;hl7vGmw1cIG&#43;&#43;oV39VmlX1wZ6Sw5Ez4gUXEqWpk4IAy61ogzFtM8SOHVClAhbWsqOWAEQIgivmqY&#43;gfE3uDwTRy1OaBmkuBzUCWNmgB5tQN/TCac&#43;Zw3k0CKKyFonRNTd3e2ewQk3KSxjOAQHYFpYP6Hor6o2LREhuHtAXrtiPsWbh7zF7c6Wsb1E4iAw5GnQWe1Ayo17Q&#43;w5UEDQiERIbKh3w/&#43;oJ9uTaajE0ixN8zTr4OxnVtedfg/IYtCok3F4QAi50IeDJhqjouIH0DC9tVLqNNGEuKIOGeO88lqT9Q0iBQWxTotqad4Lzm1FLdAhomu2QNNGJ5ygTHLJJGMUVD55wy7CoWBZAE&#43;IJazXTaRExU/WyOhhixHXjWxUFCM3CGrp6VWGgnw8nh1JkqCJ3JUHDyACryzL2XQ2mUx0AfP/uYrSS4jtk5ImyWvzyyrvWk9OUH2Xe8Er8kLvqocPvtHJTO3MQukkeJVks3pRHzrxJjNZMrMvH3kAmc&#43;YneFzttZuXdxBybv4ZiklhnBDt6YXYw3ciuNiwwE2iUOJMrhRxFShb2MqZAaks7C2lQ6lL3ESRA7CpgHFOBz&#43;FXUFoAYgtPtQfocMTmmCEo8YXvfIFZhiZhgrEcaYJp1OpzMY5XleUq7LsqhdbRXRBIfyggoCzVfk7YU32DTqKH3XR9oUFFM4fFsIhcNUBEfXOPPMtIJkLKzjhQkrwIUczITdjlbdAAXBCtA5JxDwg5YfCUwj03ARCE&#43;PakDwJ573tdORWgU1hmycDaKiRYMFjRg9awWA16yPwz3ZCAgrrffSjFvbyzRJWrJEFPWEaBmilovszyg3Cw8dT0cUoEmhNG8hEO0MMPIrgIyegOOBZBxtQREVZMG1qC2eSRqCMr6MaRILGlhwwOlPoTwhuxQzUtZh6deQMmmHuGOUkkCIvxCiKApwGlDtMAxtgQRN21hhKc51G3APCNynoHHTTilRUjeOi9BECiJVWVVt9YX5VBR&#43;2J&#43;zlu2EZFKEwf6I8VKro1K5NsJzyu7tTt7aO/eC7t/HT2vr3rf9iv1&#43;Et6zg2BPfOpznDj/ePVc3y6&#43;KE7cWzwvrP6mWf3I0gOO8l3NSvjI4RrWh7EpDXsYxPd1BGJAwPBIGrU2z/KWwWYZaZ8VUiAEkE8ZlhKwKpLlEUqrh6OT05aZJKBrSDlDMzcUriiKIicaIStYPuC5j7A9qCiwcWVjL5oxkndJq0ZqW787wvsD1ljzYpaEHinCk93uqAGD8RRwHYcOHSrLcryzs7O9o&#43;YLnGdwkfSJBKhg2N6dbn/f6oG0302S1IIJopuFmsrDn24BIptwAjlGfcjprdGWKe0BKE0coaDB6D2VIS6H8xtlYiD/VMR5Q5h3xBpTQX8ValrhUbkK5sxDku2ikZy1lTWlQSgp9IQBkwT/FeTWDEpGI1I8hRwVRQvWL1zEFB0rJYTUwRmcOCYwhwd8PI&#43;dWTj1K9g2pOlnSMZ85bRS2piiqd13PYox5of0oFaiUpDUM5&#43;F2AXGb6SoohujEHzUjzNnY0gd4hWD6tuQmaG0BIwNYTzOIRjr9QfUuYyQlpdDUgAnTEqG/RWZYDMJ0V0a0viqrtWsiDQ6&#43;Cxl3R9l&#43;aBUTa&#43;PFcpeBku4noqGH6mR7wRaTUD9ZVne6nJEIxW664CVeXKb2H5Dtnk0Nd/YGn7o5c69dx2mxF&#43;6mCi5Yj15Rbc6qbqUsamaInH/rvQSs8mp7Phj&#43;fUAEfdU9KlIRHO/cVRjWUMjj&#43;YBeOKjyVgUjdrjzGBQ5xSGd4LtQrWGw2GoSiqku1DvOQOOdrJAzEh4YR6M1w3Yx08W8wSk/EGzAOo772Wte4lswRtwoqJzAOuITosC9CASqKDnPKPQttQmXL1giDAXQsxnM&#43;o80WC364FKCetfoO1iI9egQ/EJ3gbjF18kvV7S63e7XQcz23priywWBXIsKChx53JTyrDlvOcAZBfKKq2TGrzGPUuTZDKeRZUPSkkNhyXKlHKGchyo8wDib0QIYWSo4bIs6/V6CahzlGU5n8/tvAqpI1LkgeuL0ViNq4gSAYJ4649eFoV1jikObVfdDtnMojTYfvMeofyuVqSqSAYuRyTSvtsA2/afMBtsLSYQnZKmaQ4g55YjxaAGjQJllKCdHrQALcf8HuSdWrfkVIUf0uESeULh7cLhMlElNrRCAEehXBDBdaMetoXRYg/7eqCQo3nTlA75XlOD5DLVWhezmd/Wu8Yf4cbAZbLhXbSO71tbW75txlCUuoo/NgJ4MZxSStJUJonWP&#43;zI03RAQqXKuW4FumASa2BLW2uP0NlP8x&#43;Qgnx9vvJJe&#43;LwUVkUFwhlZLC2Cbez3L1052jzL8urtq66PjZBzr9IinkxOjwRK/hGOgS9QR0ephoQvmnSxRcH3eMEr9xaO5/NsK&#43;O2QFt4G8kHl4/JAMMNMAqvGiD5kHOah2OV6UmOsQZmkDtDXWKNmHn9UejNE0dCctVg/QP1ucK&#43;NKokYsHInJdMB9UoKSFea4JW9eFxC9JZJYnacI9ret6Npt5GPLThnziKGnbTHTw9g9j67KqKt1IsbbSHn6PSFd8MTEtQRIZ2&#43;3d4Q5BjrMO30MhL/CJ29WmaoRFIt2vpUlwEefsId3ikUBP8DmH3ARBF0DmAitTCxQfdLVvOjdguwescRQASGRd1WVZOnSdbWvmnAM4TjT&#43;7jZali2KPbJ4vkV9iaUhVhMCDOMU9CQI2XPLjRkqB0kU53clMjDhjKwFGmMjCOKylh01q6BrbRGMoVunSSLwseBTBdwoJuyLBa5ObJsZY4qiqKoqGmo3tWgb61DUkjYwFdKE6Cj1TqOLsm/g8olI20XMmjFJWya4PaZ2eAulTHqgwhFiCIjChqWPbs&#43;tiE8Ld7dWlATPi186cm7A7e&#43;vn3DwYP9J7xuM838yfyWqcKRW/9tD2wn1793onizCy/qNwxdWafW&#43;7SvOqDSeCNgQAriLgJlFiGZV2U4EEHGNVA2jlEUh5WbShooUaSORi71xlO/dVSZo7FG63W4XcoqL25tkj7cNaZW&#43;k4S0Jm&#43;2MSJnDOvYRg0mOi1CsScwM4WsAY6VNJGdTlaWrT4Wdq1TFiWiqqpaVKXB9Qx0y/A8i6LARjzihFGfwVob52awi5H6HL3kQBwAPZA887sbOMtCHAauTKIADAhJvgZuHkLGCCx1vGhjNeTDHOHdbeLHao/YY5zaoc6z935nPMazJ&#43;oqNepwvg7/wGESgbEFhlXdfl8IMRgM8Pfy5jOv56gFjaoI4RUC0lv2h7v8nsb/jhBSgmF061/BGtIl2fOJyZipQGsqJ03LvaltBBUCa/ioxsR3kUysA1I&#43;2nqtGpWpBpLFhQT1WUlYCOQQhzHgt15wmMq2XW4UnzUwdkaeWT4ctmqY&#43;KnruiqKVr8CQmwIChHkrH7IqcM1zQPXygbu2dthJxg7KcsJimMQSrJMZBnv9TpYW6JYB3TIcYROwSKHUvr/XjhEqFPEWVs754aHh7XWfn1uKSUJrzn//LZ/bTJ9xdrKljkQVnOykVDHpCQGcH55vqcp5cxiMUNogNV7EoE9x7GQJKZCrj1/Yd67IHvVPLCXiXPHJGkt2owx4/HYGDPcv4a66JB&#43;74o6yiRpZZLw7YBnvSadHmvOUxx0ORsqcAbJNmdMJpKAgT5o7aY9AEQhMMmBSpmFyrkoy9a1q/W1DnvWOg3wDcYFFzD3R7kuQ0PKz9ErDB4E0FRoUcPZhuaAhDIagV2mqAil3kIPDxqpDJQnPCxQNEPD/ifeYQVucbH9g9Z11FJISqE/DJBGGCheU68rT/XycVQkQDgEcji998dFrQjfoJ3YWPLehVTTT9cvx2OvZRHje1oawA0xHKc451XtGXOzutxdEDwG1XAa5APWxJx2h/jGDzU6JwPYHeg&#43;cgG8aAKdSe0iEyhJEiCBOIfNIThZnSfOerc9iamJ99wSfHiMsWq2ILTS07mOaq8WJXumDaG/jYEwaBUy4emeebW1tqxUUdZbMWKEcydJUpmmAhAyFhh/sfsaG/57sErQYXa7g01/oE8vlbwRo6eOeAoxfMR7PUlHHXehjIMOU5m6Lgs7b8EwjQQJsCZuP4pLuYh6&#43;iJDwZD6G9z51dvelKap9q4sy&#43;8u8v2zzUdOmZpdJkIsRlWdUMGTvNNjjC2mUxRYDacP3yWfZLGaMSgMTNvGFWg/urBPOeQdFuNHsjxonydpSALOudX9ay1RxFOCpyGldP7yOgg2EsEFB&#43;s8maVSyo2NDXw2UsosSUhKtATf4LwHGtfwaqxr25&#43;gOQWZT2VJIye0IKQAA3RsejFo5GEAczABdIC2gaUa71cgnvaHTlxYr1qjby2&#43;TfwGCmqbOYKqW0wmKvcvHT8e0toqHPCugkuHdKtE313IhjkQD6PZJMgRtEIZLcsXmZwGTLFQAePNs8cPq8svmI2PpXehUBhyRxQkHlbX71RPrIvRp3u3FUmvbWbYpqoB09CKoFicc2Q8BmZ8SNrBiN4Z66&#43;Q8weG40&#43;N1zYNyhw7z7mFB6dmszjNbjYwwZXduKJHH/2qUvN5HJBISRLZjvuNUotdQwCHaDjfqvAJQRnLAH8uohFFWHRDcD9EY1SkB6BOtVNRvRE3cMvBLotCNNXsXqltk7CWgKnqWtWRQ4&#43;xBd0qACkUx1q0Nu0ohTShmFPyH&#43;68OFHkA88Pvj9NOHwRKQ0ZTe9bmr/t0OLpifjA86nyUYEUHb1TueuQjF9/4fLlPSoWDSzcObaPEUY3z50D/ZNwZs1l/49WX3f19YejjfPpZ6ZVxVNO4VccveIKBDO0zGrcrGo2hnQjLDPmdiVEOp1O&#43;2xBVtFim6Csq11f4gjGCDnwxZ1tkqbQKWQRtgFZxpD3sVlQ15UFhVaoYNmowQXUdV1CxRttg3yx15i&#43;ZZXG8xfpmd5F3rtzVtJW3B817aNoCcKc8MmjbBhuG9XrSHCat6jzSDyRnCRNyydaY5BdrWNtadiz4QqdNVbFx7e1fom0otDgdiOycDT0lw42/Z4MRSoAU6DLsoiaLz6cOSFmlCo89NW&#43;M4D0sow42qXmRrrlPf2f&#43;Z1zFgUWQ5LsvYRE&#43;MJ8cH5x7jq1fre48Ej/duv9UM/mLJ2D3XaUAeh0WK8XUSw5pFJo3aJh&#43;pWKU7yfy&#43;3/69Dj/9nc9SV9KCbqNGbmLVkcn76Q4orq/JNlxyAuj7E8Tbu9brfbg9ERmU6n29vb5XQafgUXJE2IEIN&#43;nzGWoGIDakHCgKOC&#43;McVQhdRjx8yl&#43;4Q5PBF9P42BisiTT3ARxRq3IQ8vCzDuXDwkAGlxXjoZjnyQgm2w42LaptIWaHUoSQNpZ5zx6NYr3WOOo0oYtawCpngf2V1Ouqyiz5dT/f5EXeUvvPA&#43;cKw/7l1ZLqU3987N1Pqk&#43;To1qGozfC/rW6&#43;XOuPzkeOGOJUpDShhumhfaRBuRGNeAHBKTlx&#43;FClFNkCUw7sLCXpjXL91ZufNYTuuGyFrBMjZtOtgoW3ViyKPbQE0tYdWbdjGDPh71ZzSpoNvKgN5xwsoYghHh6IJtYuFRASoJCNloAkjpRSmwqXMMKAcu4ro7Tm0xIEIHkiZaeTJi03&#43;OLFi74RzeeUSck6MhNSbFsVLtDg5NOC4QuIy1qLHf6QIIRAkKDe21QvAJ4A/mYe9BLhLkJaStmemRktHWOGiCxNhRSOEM2YRpdzjCrOtaEczQ5x92e9vNX&#43;jVarcLIqJBUY0&#43;J1cESpXn65tRSJ5xkuslbEEKgwFAjJ4TiaTKJ/EvjT3ebPdvPsS/rghR0l6dYvZC9&#43;wR87I5ZiS8y5bndwml5x02z7fLoWVrmp3zn9Wk35fx28atsnODTKgHaAL3KOVT1I5GKOgInWZ9W1d8&#43;ffQN/6pvZCYT&#43;X8N3DrJCAWjIurBtLDAz1&#43;zk7ktf/bH&#43;8Yeu/vmLlZ/P5kVZKqWKRSGlnM6niZTdbvfAgQN5rxuKjrKsqmr94kUppWdQ8UJtw2HYQDtpPNGVYsqgZyzn/PLly9Hjt9UzIVCn9btRABmrcSF8r&#43;fzXEjpmkAkmqIrvMzBMgQdjxpg1lqct1ezGW51y7nFLN2Df0uNzg8x2TPed6V/x42ltTZx&#43;j3HzkIC6a7tlc65jKizU3FgZE6bzis79R0dFXIxb67T8&#43;syemWPfTC9GSFibfSriOFZttQf9Ho9afx4PJ5c2qSLaZZlXCb9AwfQvw&#43;6j&#43;bbbum57ht&#43;wj5zj3reWq&#43;YKEf7U1CurhYLFEIApDFvU8jJbNoe3C2BHzJbAF1Ay4pT76TUVhJjaKnQod83OglIlKdcKKUWFQCTiG/zKSh0CGq7l2SPhzvoxSL4vAWBgNw/FI/YNNENOQF68gJKvIZwHYJYyBTARhR/Jr6pBPpEyAfGhqJt5OiMMSIpGVfUMcKdkDD6DDWa89HWFa4NtQgoPJMdEU63lMAJYUNmhoSB2odcwgEbnoYyWxCAkncGN2DVhwlAi4DJkh/ya20/s&#43;l2uG1PQ0SalffZ857Vwrt3L/3gmJjeyDZ&#43;0p58X/nq19MXSsI8I9NZyoldT4c3q5O3qlMjX62ImhDyq&#43;aJ31t6PTalLGWVjxGvICyUDQlPAGsablOFUHpBHDxr176WXKvS9FZ75jq/8Vh2Q2rnqbQwzKThcIDeeM/lV/ChruwlbX1/OFpeRkZbWZaLus5XRmVRVBvrW2dP4awl/A&#43;GbYqGLULAi4LwBI5eNmXRGpeQbohIrXhK2oFEvUlqQhnc6FoJiach38ODBUNGDnTA7l5BTJpE38a6rtUcFB6KSmuTHllCA9FwtuVZkiTRmalSLecZq8G3iRd3pvW/0Lef1en/sfrCFxejT05X2Q4TjK8J9esn/uJjW1d/fXv4D4&#43;80KPu37&#43;4dtl3CTsqk9R5WpAt9sOfA0lvemGyPT6/CZYIPEk6/d5qd&#43;n8JfslfozmmfPeZiIbdQGd1Nl5&#43;exf8lvvUKfPicFnureWYiBg1Lf/2FHUDPG7BpchhIyOXok7sQVL4n1pEyKw4cRZRzhJwsYIYW26PDU4U215/yhDR6Ev28m4EE7AyFPXoRDbWMTWJTa9Wt8v6KUjSZ4oE/1MdEn6MDflYjcsAU4x73YNlgYtaj0CsKGbbWwc19k6cuAx/EorskxmKU9yj20I/tY/QIIBjl4k&#43;KzGlmaz8TjBTgGkIsMEc3cQvwrZEQ7oY1scCcpoSppKzsV8toh849ZjDi&#43;lKJveevM4wBx4uDxgjAvry7Jg453/mH3ikerYH6k7qHHvHT5EPP/d2au3SJZyOkjZ3xLf/Mzo/pNkgATuf7D42rKdfzq/9Xudo9PpFPvbred9TIDXVtHNMNyjNg&#43;Uzw5JRRlLJCr6hkPyfvXcwBV/kr/qL3t3WmczmE9gD9l7f4JO/lP2pc8Uh96rb27HcazZS3U1j2BDHs7BeEI1bB7U95Q2PlVCSLHcZ1k2yrpJkjBlFvPFbDYDHKsPD2TYX15ZGY1G4clPZ7PZzDoCkj0htqNsOtKSwyat610LyJBag4ZzAuiuLBf9/lK3n6apAOmw7Y1NRMLF1h8qjGsdFmJ4dwkqQr8qm/6t/KUPlK/41jgs4r/VOfOG/vg9546fV8lPLc8fWC7/fFN8Z75GKL2ve/5Xlr//ickVf7x5JEqdSIlEEWxValCcJwtoRjDGofeBAroghu69SFiWhGforatrAlp7PZq28qsRD9xI0qHI2Y/I3Ne2QWVh18Y3woDI7iJwREoG9a0k3qeO4BvC9Z&#43;Eo11yzktnwuUB6JVlSZZnDNAHnXkzdtY62sHCZ2drG3M6SmmKNFtE9Y0ENvPQSADQXeFcWczmDvNQ72ma5iBOqpVmRAInleKfOAzD&#43;KwAIBSOXWSzQTYh5PIq8CRwXEQ8NEGloFwKa20Fej8mIksh9d2cuXbjwQ14RqyjAs4zlCwhkPMTEPJC&#43;QDEi&#43;7OfoFME3ueFPQLgIrFGJusb4o07YB734&#43;vGpXd8umz1wjv7&#43;he2pKD91&#43;6nlPtaFI6Mi&#43;qZ5byX6cf&#43;cilaz4&#43;uaYn3d37X3pBL50v7LQaZ2DJEUEXcAwJaLQX2gDAKqMyoZX&#43;gTvWtRo8b/EYCUHvBXa1dXZqZH97rvu5nxUWQO1Uh9VB&#43;WxnZZ7QqjuusBlgZYinaBFiuGwVqkkqoHbSLXQpwR4PtvqArEfXZ85Pd7DJgWJxYSEmIOTh7Hhr5&#43;TGdkOBYowpr2tKd7CjRn3LgxGDQRobGzIJhRPhskMGZFbMtNb1uDDb8w2&#43;vntoYhYXfYcA94Yk/jocZ56Sytqr&#43;/UvXHPhN5888uLkLA5antmXHCXLly7XS1L9zHHJbKqL&#43;XRjTjh7ZDJa5jednrO75fZX5z1CU&#43;KYrajTPvNUUJl6iFEJJ0mctSCaELtHMu0ANi4Lm1CrwrmqrohRc6fRRSZU9FRwxqmAcRdurU46GAzEoEsI2akW8/mclAuIfgA1EZJyHkXXOmk4PghLsyz3IWGhhfLer46WUDK1qqpqUi30Ik74WytZOI5n3jkNcbVFPQH5FO1vwMdYMe&#43;JAAgtvAb0OZhuX9r1lMXmE9Ah146shpRhEX4t1ZYUhBirlOGd6Jzrnddg/kpAQNYaIylNCUx8S6WnC/A/MZT8jY&#43;RBgsdPZUZaxGhHviciDhBT&#43;Cui4r1SBZrfWVRwQRXqms6wOH9bE/RhxbV90P06PXyPN&#43;AGg/PGIfuvogoErQpl&#43;hvLn1nqZO&#43;aAeJ4HeuzJ4ZyxW6s0bHH1y/9rv6OAQ58h/XPjn12a&#43;99Jq3jE79&#43;Gjz3S/cUPOEIPuU8ygZh07zcHOzThabOlqTAn1MIEetYS5NWcr87eTMd9nVlNKfZE9fTS9&#43;it6kUEoOCvyDbvJ3u9/&#43;ljn4wekrI2g&#43;ainBwZ9l0dmA80htR6oa6mYjsseFqIg2xyWg1khLM26jBzSu95FqwybRfAzn5AlAfOCNLNHFgiSVyFo/5CgTBfqYHjU06oKkadLvdbtdkYWtU2GfH9BCEkdlsCyicvLWDAjrLvHq71y9/ScXV6Y08ySc7FHeAlAPN3Xt21f1U1P/sfEQbwhQX&#43;Y3jp1aTsiXZ8v/beeYJ1SgmBu06Lw2NvxS045tKHgFEdgAAuaiEaqJ&#43;FBYgcUCNFsIR0W3dvZeh9WoPYFeQDfnaerSEOuSbo5EyFaoADHDRV2gek1YZrMivA5HaZr5&#43;YIIwRv99Jb0s9fla1cCtQ0JKBRBaTt8SrK0LMuiriLNkGBU4ivDTsu10MCQR&#43;591MAp6pAlgcQioYAb1xWsHBHrpmYYgKZixEVFezwgkiQRS8cP7WKtomxQ&#43;BfT6VRwsH1BlUPntFaEkfnWxP2IMXcEUYhdXULoWuHjsN6medpZGoSqzLu6rheLKZls4x7D3i5JuPcJ0v08PAJr3a3k3Gp5alZ3P1C/6Z3d5zbU7LfW7/jVg4O3H1576fKR43l1mBcPz0af3zl&#43;Rg0ET&#43;7sjX97&#43;55ktX9Pb&#43;NvLj/3/vFdZ/WA4sAGhVN1SBmJIwz4ljxLWN6jlN5jT3MYlDnnrXdHynN3z564Jp398eh1i3l&#43;1fz8jyd8ygdA6giX2PcVN15wdv2ye5mF/EUxxOvDtHlWxU2LbC2UC43vg0UTFpxja2dUTfodHjZS1DpEfB9jrJwvvLO/tfnhguWPixOfZjc5SMyIdVKENM8590b9xE/I0y/ztX9V3Su4bFG&#43;xBBmqUc3yX37caI7n8zN2KFlFmI/oMx1yqoa8VVQaPBr9odFT8lM699xB64/Nv3VwbqiwrEM8AVA2HT8Nn95SG3nwKGfGwofvbKcJv4rs6M2/CCfdMxWSN/h6LTCORlZ1tW8AVq4UKFxQgSyn&#43;pwGnJPwgkumqmbzvoD0IZCDHOE9yA5XkqpAV2ksUEAUTedz8IaVrFyURBGYKyVlEXhQfC8LzKZjnJAFG2spgiMx1S/tddNoUBtiWjt3tZljWLU2G7M8xw162WWopcypuKMMYT6LkABxjhks4U6CQ8g9IWmWccaQzU4VAAYcbSy3G54RHFgZzjtgT&#43;283Vdl0VhUXGec7Fz4QJpfVmjtSfUdd0O/oAQWimMKyyOXhqnxsZktZ3Cefhf67/Oo32TVlrXYCBCZTg2hksjgDYkyEGtqso2XDDvfafXg/qQ3Kue/D45ccRtdLvRWHF1bY3Q7UuXL9PhnbfJCz890nermtYrq97f5s7N/erbVk4652&#43;RZ/fr8rcHf/6e8/c&#43;Xw4QFtrKeZNGZ6eVm99S84EreZbjLZzlK2eWHoxsbh7ex1c7tzxDjoTLq7VW6pDeOpZdeJodeS19/mWymqZpkkl00zHGLB3I0D&#43;5dbhn0DnMsgwbeGCtBi8lrAQzJXbXEQ4vLx6C/IifUFXmbnEmv9FlzXSX2jYgEMuVUo/owRRnRS0Qxe7KGxhtZBIPBXSHwvRmvrkZq0Qs2Xk4Qhhj85OnSLdLhn2WpiLPzyTD/9NfSTyJCwngBDn1D&#43;Y7E5X83vRIx&#43;bIcx4Q8x559lE6/JzcD0hB0YM&#43;Kqp5Ip0dZEn372Zn2DGB69nY3GxdkSgY09V1betaTYFfFaozF3XpYH2C2ganwGwjEty669pbOxkXRAjMYhFwii5zopst4OOc68A0yZehkPGJQHQaSAJo0rrkVhXOR0iaydbaopnFOGeJUra088V8PoZsC4EGBBTaOh0w/g/f0xn2QTe7cTBrtK8wdc1EOIjRJRPDzNbmViTbt1hdOJenk0kIPADXTbPMJVGDUaz297U2GTSec&#43;EB1WVBHWWKE4UtdmdDbE7qbDfHQzRy4zTK2k4yMuYtzq&#43;7fXBLgKPSu4Uni6IkZcW7XatUdGcFNQ&#43;GbR6IG9zZT6QPvHn8We4WlmrBjJC6KsrKT2u/zaqNN648&#43;d3i6H/yN96Vnf217lOPq30f2rxxRwtO3B8NLv9&#43;cdOXqyu3OtJzFR42dm7huOm4yEAIOwq4hJf98XXnNna2wyaUoFeWilAqpbI3Hw/sIBsO83Q1JHvGFkWxsRi&#43;2x4ns&#43;mP&#43;&#43;/WqQ7HIJVJIj3IcIxRjth7yiQuLwtdzRIsXTx6XAjGM5EMU875gAisz1mjY4hZA6fs7u3HVjdsSZIjstr2G8/bVacsdYRqDX03RqjvQNcCcBGIyN9LmQ4vqS6rWhuMCX4PhOsVN9/WsjI1JNUWkNhX7X9FmqaY0CptTGmOkZNvzr5Rki4kvYJSdjQvjyXjF33vt9LHFsUBBzIbfRJqrNex8bYVT5MlrcsocY792BAA0J&#43;Z7jqetTRA70WaGpiN1ISQNOy6NOzkTnHtwGN2EDYYdK3g50ikl3rnheB5qOLQfddvz8NlGqeUKqram5LUJdGMTBTpdNggddrM5gXRhqZJOugoo2KfXzA0l2&#43;QlUsIjEGeTCsCU29PmRDddNge2UbDkK/TbbHxJCIOpZcpErEI4fhyEHNHvOerA5FlIknBG7WBaBnDq5pYy6EZ1nJjQ5ZRIyIJcOZ7dPlEhHEju0qHGgTxrt28s&#43;ush34CUKvUgOSLPrR17Ru28F5skFC1gq56YjRbWQ2PUtehHBey1&#43;sNRsNut1vUldZagWg1A7Cxiu7O4TQqjd2xmMno19unD5Etu5g&#43;aJ68Kpv2er2f4y/3uH14PJzS6UNi6foq&#43;6nec&#43;d78iPza46lxfv961&#43;Qo7rTF4Do8q2YTpMdLRaL6XRqEapqjCRaW0I6OVIIbuKbv0yefW/3deudlamepGlazabb66ejsy4CIYS4qztZ3tk&#43;ukq20h7KoHm&#43;67tF0dsOGL8aike1uRkBDNBcsUlS8/CStGN4aKLUi9/V73c/WT9e&#43;/rD2f3LevHb9mMXSf9fJz&#43;7GfaGdqp2lFphPPdpmnayQSKk9Fp7jvoeLVLKSUStmehrAwUOZez5H/ygFTqPrxne&#43;0sXN5DjGtEKUm7z/nfcgwVgmDllh3L9gSsePqUH/&#43;zs67WjHh0n4N4NYCbvI&#43;u/YZ/66ODmc66HHGOKyTmMIStbteioFvXZEiQ8qkkDkBvJCRI0q2L6rQzWtx50z51SJCSg1BhVA6&#43;IOCdBBFJQBsBRGGrCTKRyJssyJnhZlqWnpiy9slVRJIPeLgGzRcgRgnrRCK7SCMWN/iEMn1v4J5BR8n74CbPFAm0TDYQlJwRK6tYFQEphwhLdrVx4C9XFi5UQjbsyJTIGmDhA0mEZ1ITsBcbHC9hjzeOcE&#43;UVK3urxCgd6pwqylCq0QbeHSG8npRlKPqF8Fxet/Hy7SefPL164sUb7lxHoWrvuFZ/7Yuf3l7e99KJ6244/YPHTtwyGy5RKXgijTOz7fHs0uWwRpdHu/Vz2/RPUu20J6hRxORwjTD65/b&#43;g&#43;Jra/z5z7gHh&#43;Lhq8xTH&#43;n&#43;4n/3ZtpPhfd8Xn&#43;RXXuTOfeNxdG&#43;SS7V/M3D7/zW8CvvPXfrI5MV1I5m0KTBsU2dEYeoUClIlhDO/17&#43;2ApdMJaDm3MI2Bt&#43;&#43;Aa5/tljt2db28U58mvJs29eGpRUOkuNJ4y4AdXHywtyaf&#43;76kd/a/ALhpJwBEKvu79TMwBCwMyfOegUAbiia6n1wsdIa4ipoGpYG4WvsEYgPzr80cX2&#43;Opnzp33K89cc7/39MCF9A3li6/vz15ZfvkrnesektdbwjLNRV3nuRh1h6uL8/&#43;y&#43;vij4tr/LspCPQ8AADj6SURBVO5euF33Bhvyu6QHjUbCGVYNuC53/cfDotHx4BjkGlcVpXcMtn5x9aQBaWJlDKNUUHpdd74qyeWJ/pX&#43;55y1FMgpiUws4YZkzrrr84I4/Y7xyd/dunPscgJ3hyO9EFV6aRN0UXjLOwPiMzPk/SaMc&#43;mYLVRRmfAcJjNgtnncxq2xeJpku9OiuXKuQrc&#43;DT&#43;/jmK3Lh4ulJJUAO4RuXScpjmjIU1X4/HuItzbRASnrpgsJAnBHhKlqQJITFWpslFianocAjckh4SIccLCkZVmHQRvAr0B&#43;vxIxUlT0kjGAhBAIG6fov52qw3bqF4zQlu2GQy3gRpBwEkMOrQgeghObRx&#43;ZrkoQhXBeCtZghyd3mgEI57UOXft&#43;adHidwSXMl0ZRDZJ70LZ7Wq5Xi7SLMzywfu&#43;c5Xn3jlvReXVoCWRVm3m&#43;QrqPmMZzCOcL33iJey8xK7beG&#43;ZoI62u/3U5cmLOE63Ew36d6lnnilfEER1qPF/i6bu&#43;ysWfrF7tcZQE6uSYqxTf7O2vPzpZ8c81VE9tR1bSDa71g0aKYtNujf6ftC1tbNPfNKIqomFIR8Ov2WPHy1OLyv3Oq79RXqMsZTzkQqPRNquPY9P/ywv8EYGMw7h3LekbcUMbfQPAb1jNrosizrsiR11UD/4MTd0K38UNODCM/5erp9oCs&#43;TG7bOn&#43;BOP8H7qre7NTXjb3HX3preeHWzskkkYfITEr5QPXkreqllFhi9Wv90&#43;fSlc&#43;ym1qukmHe1vWsKkGkmgNgSJK9bCpEejemp7aquRAcRD8udA9&#43;wN1aaYuU7NzXv3f4K7ne/gfP3vrNyUrEMNSUEfd7Nzz6QrH8ny/dSJJcgJNoOM2X6BL2RJDWBwikEmWG98Q6RPbSwRAjIWkQ&#43;RFJhoYpOJtAdhrM0nVRtWQYnANjxB77kGFyKFskQhYAq99ZGYVyhoT8Sy9K8JoQNMsWTu2SmWGvYnd3ZWWltcLBIRPOWdi8Dr8XJvNYgNRgN49tYZkm7XNFP2cB7SsH/o0OhLc7g363293Y2mzd95EAi2dr6ugu2wzAVO2gu7W2FEL0er1Rf5DnuXCXZxYFVlr6lWuYlgA2wNoYpXk455tdRS5vEErloP9z42eFWDxz598wMmfjzZnMbVVfffGFnixfPHHDZnc4J&#43;zGJ79y9zc&#43;&#43;xd/5ZcoE55Sokllq4pUebfTOvfh2T/ntYZAEZ4gMF3LrWGh659Knl1zXsjRzyffvzG1Uhx9ir7q2/JBmaY/zx75MfPZ/yf9q//T3&#43;u9l0IMmZq5UE1hwRfvv8O8T/DvK2wfWjyHQ4SF13Ni57uy2vmqv1ZbL415oP62ttkj&#43;jpa&#43;wnn79//Zkxx76lf&#43;j49MKbZXl8iSmkmJYqq4sKr&#43;&#43;hAC1rQnFVJwvJECO6Z4Mu9LnxbCxsKNX&#43;hWntbAbQ1VdVGqZ&#43;mJ&#43;fuikeqmyDLoj&#43;/&#43;Pxjw8Mv8kP1tJha878f&#43;jlCyN&#43;cPfwWe/Evuq9&#43;uHdPv7j0h&#43;TDO6z7CXGbaDB9IbEXUQmxruuiKNB2DBEU7VKLeSwG4V5qIWIoXUyn4FWbZ6yXruX1b&#43;ZPXC3EH9Svu7y2csUSii0DstD7P65u/6erD9&#43;wXPypeO3j/qhSCpd&#43;SzYIZT5MGfJ&#43;BLS3DIeoF1zVraULDiYJgMCtq8NXAF9KbahsHahkpJ5AKRGWeMi3O5EP3N8/CCnGrAgbtahsYwdfdyhjnmcJX8lFDVBNcOE6yjvYF0A4l2o&#43;Z8&#43;ejTzh1mwZvi&#43;hSeT0xTGKzATHIX&#43;n06Gc1XUN2olZ6n1RFKPRCPvbVVWVUDbOpsVkPHfgb&#43;hhwJ1mWbfbZYC8KLcnFagXSQicwGTiuFO4CHkzvq9ZUY1nC6ATVhUOgXBBoy6E1joaMcGWRhYFbmDTkx5gQAcWG12nfrB64txkcffWk/eefuLPrn3thbUrr63HSX84ufN1B/NeqFW&#43;s484l&#43;V5x6jbvvKJl&#43;//6eLQEUR1zmaz8XhsyjJKnDFTW6uAz6iRdTyfXrL6SwdvfVgpHIVe8sMvOeqyIYfbWOHzLMs2Kzay5ymlR9XOv8r/7JHyxL/dumvbplH5CVHEIpIKahRqhYMJVYVvFmf&#43;//ILby17m76rDTusLiaODtLZJ5K7juv103TlNeT8SbG21T/yb7Y/9Z8O/Ox6fujaxcl1m13iS1FZRoqWGIQ6WwrGPBpE81xdq7IcHjyAlKtWShIZMOnAg9/bApSuo8/uoCt&#43;bHb&#43;fLb6z3ovEGeFXtxMzswXs7q7JsuERm00X1fVQi1qXi3ctC9AuYZ66CzUu/oYmYjzBaA&#43;I58EmaXtRsIoh1RNK8MhgrNi7yKG&#43;cfouX/Uf6pHFKH0&#43;rS4Ts5b1jTlW&#43;jgR5054i//ffU/ztoD37GHn6wOX/CDy67XMhCR01ZdvBix8Y0ObiQDAc4cbBNVxH6j&#43;74Mb3oO9UnITrOMpDmoroE2S5zxh&#43;1XAuZ889KpOGnnnHGZ5TEjmOpKl6WejGOFSYhLMpLn6xvr7VRib2qATPJdlWUsehlTmxNsJhVFQThLwcm9ZdRFlRil5vM5fttkMmkbUXHu3YyRcbxU1/WiKKbTKSIgO1TgEYBqbWhIRAhB6WzSgEbb6xSjW67bqwWH0hxKqbooYUU6HMF750CEg&#43;YyqevaaXPtpSc76uJ&#43;xd95&#43;jOrs4uU8585&#43;fAjyU9cXZ96evVq&#43;/xzYAnvLu8/NE773dMvvers4wfGL&#43;//9Ae/8uDfLtaOjieTcKgw1s2H6TABJGBYNOXOuEzqEsTQnqwObC/f7sezgspbtp5/Nj/wbdZ/l33p6/lom4aFuNo/VC9tXlnZa&#43;gpQsnRZNzJ99&#43;Xjh/aGj&#43;jjwOrhngWlRZcEfZUNUQhO&#43;Kcp0Clkp10aSX/l2fu/1p9gnryO&#43;kfXeHOP&#43;pvyRX9a&#43;rR/7HvnT9/8v11svzBQ3/nQjL4&#43;zt/8o9n/7/v2vTXF5/6ML3jGbuMiIO2JZNXDo34OKN4XiIRZXLqWTBVlu2S9e0GgwNUJEknzRKRcMYf2PzWn6nVP1560/3Fk7&#43;iH/p4dt&#43;/G/6jbH9I7Zb5t3i9OHD4KEykl8xF2x8tHVw6JndOF5Oq9sny0f2Us1bYTVUlsPgVLBoOw2kAAxKDUIp4hY3GUt9KA71MRohI5Gri3jk6vWbUv3j5hvccvNgT9p8/cwjg2yKTIe&#43;oRhkaMPxhknlvz7nuYbbzk2TyOnPpGbv6&#43;frQd&#43;t9WNFhfZkO&#43;8QRqkPtLBzbVQvxTjDhiCsBoUuMJ44RL8liz&#43;5y3s9qYkrjnMExD2uEXHzkMBGsAMOhTYVnnlILFaOzqlVypsDionAo6FFK/K52XGyPM7ZdKNIoopJWeD08MNmYuVKv3aKaL3amCGvb636I2z5lSaUK1Y5mGWcQmYgxncGAMSoZi9s6FMwkESIEW4&#43;DTw7PjHmoqDc3t13TCo8/DfHeOBlr6ZSY4IUrXhRozMnAXT4BsTs8tiFcLG7ZfPpSZ&#43;0PXv2/qCqUCLiI3/j8w6E2npxZdJcYF/sWm1dunr3UWzvtD9XLB19YORhq3a2L6&#43;kQZwbEmLooGBet8u3hq69GleOiKLovXnx6&#43;cq/8vTnHt1/23kifvbkIx89eO/J2eQtybf&#43;4/LdA8k6m2cfXdAPXFrGOfZbDxWvX2EPrR985GKfjE8CBjgVUJm0ihxlXRvGjAXoRVmTujZkmh3OvFLF9jbxpH91b0Ws7Lw0N7S6Y/ny759&#43;KUmS07b7/IXJt0161F8c6WefM8sP5Uf&#43;efdr/3x267Oqbylrq8rSNIap2OFATBilSbcrGiFv1ugBeO8LDsjzqjLz&#43;bQOkSdz6qj71vuSB9X45ISt77CdHb4x7ozxpGeUDlL&#43;M6c/5p27zp3t9XvXbXwj23gx9WWt6tJVOzs7HgR0m7qOxP65tSB4RkhjhtiyW7ASQwKDOn0ZCfHU&#43;5/ITp1gxac2Dz5ZH05lUhQvSWnfvm8D4Q6YEuvKoSSc5dZ7&#43;&#43;vT624R2w8mFz69c/ypagSQvDnZo7xfO0MaV2SMw9EJRKsoq4TLDx8dY6NuD4EWjDFdh8i2GE9JXRPsfjvfanRRGPhmK0NUg3HOce3aGnLfvkMhPBgF8hLAbwVEy6THW&#43;CEj4UkPLHFguwJyq0sjt3LpWv3PCLtjHGMOexOuWht1T&#43;0hoMiFKZ1TWZRnD8fEXvYwRIiNtLgGzRj2ntSVQr7anVNkpTsVj1xDgeVyakND4Qm0vLQEImSpt6AXbFV1PraOYVimVYRKY&#43;57RuK0x86/kt2XPaz7IrEzJxw1eLuU49KpxXvfmntVdSTO&#43;2T17vnNgY3Pnb1a1DQHIo/62ezRrgEhPrAhQgfUHH&#43;AnB3wnsdnfr&#43;vn3XTXz3/pPf/sqNbyCXv3qTOPssW7pxe6uzIm&#43;abJ7c5l&#43;66bX7bzzq4B2sOnNui79U9IhV7NhBB8heU81MYXE6B79CtBhsRjhJOj5NTRrSS0IFsaY7TIedDn26umu4fXifTc&#43;y/cv24lxlpLtgg0slOTN4xZsWX/tqevfPbH7&#43;78n5Px68HZ1sIgQv4QgMiHVBEz0U8cpZZqiIyuqoq0zIzhxs3VLe64hR2FvXzZ/4885bB2zVWivHY7dzIF86&#43;ho2/8nz3/7wkddsz1xF&#43;UO9OxxxHcpP5OqUue5Rd2LkZw&#43;Sk8RJX&#43;nYgIZMjZQA33XN04b6wQtfqjkDheGwgaOrYwggw337WrmW51z3UTKgGVsBq5qyqrim58myA18SAFyRbm8FUPSuLo1lbmDz7xVr31Ujan0WlhdrHXHxEV3e3IhSr6GSJFLSkAUzlnUGyLdz3jEYwXgKzYJex3JukKbX7w5XRv2jrm3ntNNHtJ5JkmR7OiYurFtPLAdcCz6M7XNnIlm/kVYnBs5Z6iKOsGG8UrTakJ3WSHWv/gkVpBUA2PUMgE9roMs8wUtK03SqDSrBOk&#43;9RZoRIZ6TrB83pEXn6ga5Ae06kkmWJC7Jo7WIUvGavd8VncU5cA0VM&#43;xe0fa&#43;iDFqexu77uhPTxpLCCIZsfYnNr96unv0aX6IjC8vCHvn6Y9y617oHt8cHD44OeNBkMGZqK6EPcjcVENbbaVDBsAQY0woyECEvdUKMsYoa7B5NhxfSuY7ZPvStnKHLr5EDt5y2fK50ueXD59L&#43;vV0etXpZ34g00dPjz2bQYmbpv7F87PqfHbn8MjhyQ5cf5aRTge5Ndhqqja2AHcdsrcuaAwsLY0JIaurK1ekV2it084TeV4dvvLobxx/Nmf7c3Oil/WGbNBzvW&#43;Ze76W3C7U4iCdTpV/Uq9dPzvTG21s8VFbLGnDIm8GoFdtI83Bfg71cFXhxDKObcpwIPI8Q8JTWZakGt&#43;/&#43;eW6Et6TJU0mevKK8qlXM9On&#43;dtf/kIhFp7Zlwgj1m94pTO9pfkZ16mYz/M8MzyEEQlhDTHGUPJ4gCtIoBkapY1SKShmxGQbql8UTtrc3MQV6ZzbCDF8G10LBOOWWe3JM&#43;wwUrGJs5742VYRVi2hP9etHfNlVRaVdkpJkUBUj24MbX63urqK5mPtlkBg6WQy8TCscqDsKYSwHrUg94IrGvhH&#43;5d2/NN0cRnnLvxkbxthMw8JZ76yEp5Pv5skiSRggQ8owN7yqNW1VA1K3DmHaqSt4IltjIVDft8cRmjgEN&#43;jlGh5UwpBScjCGBSksjsAMrrI89zCHAT7L8JT10ytcACGVAcPBJgONOT2mEibalG0JfpeaR7R7w1x3MTBwcg5V4G1isu77Uw47HhrnUIRyXxkZ69ZPP94duJ3Lv33g&#43;XFU&#43;mRc8kSq&#43;vXbz/2L/a945/N/zDxeufUBWKdmu1QYlU5n2xe&#43;pmznztarv&#43;3K990urOfECK7Xa3rcjYl4M0DCuA0ZlZgyPDql760mig4WbxJvcu637rm7nG&#43;RCitsvyeM1&#43;c2PHnV197xNiVcrotE2kt1fzldOmpzJb8UsIB9M8FZ9xYb2eL&#43;XhMrF1LhsZSpIMV42rh/Q6ZqiPyLf1HHkwFsX5Nzirmf3b42CuGOx&#43;9cOXGmfOH70vObLjN751DgO7N/Pyd6bMf2755kiyRZH1jzpyfx5BHKZEhj0A7DInGnIDGFTSz6MEBXdmQhXlKLBn2V6D&#43;12q&#43;QPmBJ/Jbzq7efHIcst37/dN/ffqn386u&#43;cLwAUapoeI3xy8Sr7udlHBi62Q8s7LbWeutLrNcLSSl6SAbaADFGeu9cWZeIJSFSdkBfyrHWE2JKzQTHsE5HDo0EvDANuniqtVaV6D9AatbWa35SsEc/6X6C5agFxSk0hluLV7by8Yn3SMr0okQS4sK3f3Ruas9IGbh30EWG6p00OHCmS2FAjURxDLHqBI8JEROSM/QSB1EPFAEm5LGg3fvlnZOO6JJBp7JghIhUUgUOcNlWZSqJrMxZEaEpmkfmE&#43;nvv985Aw0PXAcy&#43;ci&#43;ZEmVvyvUmCHCNGXLGWoGVQUBWpF4VZH9ITR2mxtl0nCYLorAGDDQx5tOZA64SYigAQsGhjvZ4CKM3VRzWYzh1puWveWltt0gJHYUQubA029KPSxOLAx2w5YOAhhupGB1RIqRTrG3rX1zb&#43;45m0Pd29909lPH9UbX&#43;/c8KnOHW/ZfvQ7&#43;dWXs1UpJbXkb1/6FCF8pCdK1ddOTx5QW8fHpx2jb3/50x&#43;6428XSc85lyRJP&#43;&#43;Ey4aBnS6rxWIRDiprs8XkZrN9&#43;ugN&#43;tj1c3vi2ze8JrWkzrvcaGrUbS9/gXvzhSveVIvsImdeJveefqbjTCntWbZK9y31G8Mo0wiFwrQw3MBsNsM3kSSJBXoRbrY/PHv7I&#43;tr2rvfv/ULN/Y2v3J5&#43;eQk&#43;&#43;Tl4yxLrfO3DOe/c90zM9Nh3ryKntlvu&#43;/Jn/qj&#43;q5n/a09vkYb1jSlFE9Q39ADWssPU&#43;86M4CDUPi1aAQnpewBVB23Te3sMXvh7x148Xfnrxvy4aH&#43;oV7de2P12AOLr/9h/lOz6UxTU4op8b5yRU3qhZ&#43;Nyy3K5nM9rxJSsQo9fghkriurq3hmg9tzvVgskAOMzQ5HvEMaRsitmkoM0zOs0JBYZy3JMkGs8/z/nl8HEoUcj6dCguQEpb9ZX6g9mZ09M7cyktd37TwpUBeh&#43;I9G6xw5VQjwRLnCJKSvHOdOrSi8m8yRzeYoFYnsdrt5v5dlWZQNbCeRLb56qUsISXQ4g0QJQbUOAWmwvJykiWe0qipTqVZMJu/13A9/2r5aq6rpWpUFlEMWgoHaBj7D2XiMDOf46JwDcG1sdhiwE4rm46BXSGujlOIOnj9cfFgk2jBAgFezbZBzSAWU/d3hENfGZGccPdwa4fjYG4/CSCi8BGTA&#43;MIYJ94r55X3RYOUopSeINuazD6eXp0ZO8r1Qbkx7JN8tMxI/zsrr2Xa7DuzuaDdP731Fyml965//S0vffTFpROfPv4zeLnO&#43;qpKmbKcUEdN6XU8p51DmPh0VmKi8O9u&#43;IWKpWQ82wLFHgJ&#43;Ait6/JpzX3123/Uv77&#43;JibCCKlKf66bPVsPXnP7qS6Prv3r4ulIwQnyag1QN0LWJCyECj&#43;IazPY9Lp1eOD7KHtuaW7N6Bc/2Ceuelrc/PObPyWueVTYf&#43;gW3/2V87Rs7L943epkDLzclbNMd/ej8dWfcAJeOAT0HtIAriG1l3GQicwCZaq1FkiilyrJUdR2iTgMY6DgSYh18VA2OhJ59iRz/FfG9Xx1890m7L0sP7led&#43;9TTl3qH8&#43;7Bm0SW1ZN/Sv5caT0q14nZubfz2I3iBxnjYOlhGCggh0QUej9jVoWqLJWUMi0TzwXpUsl5p9fdLe2Q1AmHTk8Ds8JEda4WCOGor1z3YXetWT6svdVKERB2JApE/NL00eSGb2VXVmLAG26zqSoUZ817PSQ/KaUGiwqF/lsLstoZ5y0MPKgMxw61xsIgCzRhnKREdAj31HvlVV3VGwVS/FpJ5haBTwgpT65TSMt9Y3mFnR2tFguyQK0vGs5KovdSF2J6SmJeQIg2jqDeZ5LTlLY4OQPWmcgciuamAFBBUX586TjNQQVSCZAnW4WHOq21Q2AvIK4aoWUWQmXKrfeVsQlmQNoaMPeajYsZ2dxVIMfqBpuUcPEixW4eop0pbY08WTMBbglWiA7c6lz5&#43;/TKTKDYuszApecN6qm/u/1nJ8ylf3/4HVmWGZfq3nJ4Q3lfCOHTzkL2HHfo8dGH7l&#43;1KFrrQIERHi5uc7aDF2ryPEchdBYl1&#43;DU7Hxm&#43;W0m6maCKXMaLu6ZtRu&#43;t3o9QhgJMGNLo2E2k&#43;V5jnxmAwCfHqrKQQpnYRa3mM8&#43;d5E/NvYTO&#43;GevG92FahDanRL7A2HH1z81Y9W5TKbpbqstBkX/FTVA6IciZmMZVg4KaVoKuqqqtFhxPuIcUUjmDzng8FgOGSC13W9mM0WVbUzne9yxAGRh7zfZybsev/0C/zWnXL8evb44&#43;Ka92VvUE72U&#43;GT5X/j32akfkf2tTfW3/iz7J6v5XfvI4tfu/QfvpPePBqNaq2KoqjrugJf/Ars1GARYBghmrEKjN0b6qmIsuPezwptm/oKzZEQ400Ef7d/PRGciSq8yFYwcBTr/0/JW8D&#43;T2PIjXbVWpO6LheLMipAuGIyjwkwqhXDO8OoVTVa3xEyicJ3ST9KzOyOeXjraytaanpTY2eom00jOqWl76LdNLofcSmEF0ozR2lvNGoDOGllLbwf9vqIHkOzTozDIC4G8xpEcQPDGfVeUpCIikOcZhOF/zvZiDBhEK4gYNkT1nNZefR2aGYB7b1EDe1G6SVakDaHVCu7DwZaRNS63NMN3yv22ai/R8AnNOiENIT8o/KTias9Ia9w54tudm/12Dm28vjarUu0vopcHHbrzJiFBs9uVg5Tm3RYenTfXZtP3P3iF/7LPe/entf1YpGuDVq5mUj&#43;NBXRRowGiOMFi3BbVirW4fhqObyBRCZpdPoxOxOI4d45HxVOsB5loBjliDDeIRPfaG9MCUARhxAFGX7aQ/W&#43;h3ZWiWDEKxD58tZi0Ic27umw4ErKzlHKbGqtMFp7M&#43;Y8ZJtOcAr&#43;6zQkUZQK0QGCGGQzcJowg3cnsoxUiuxslnQLV1sOdyRYHhefJ1554HGFrKRO0ot0eVaIUrLPmRP/tb5P0uI4nz6VrXyJXmMIyL7ztE&#43;GpGIzU88c&#43;1&#43;H7/KUkdkOSGo4koYyki801c5D5m4R18gJsY7n/V0DJOyio1535giaS8CZgsu//c4EvI5xkWFTx83Ubn3IZPv3xWJBhSSii8lqhEZyWq/IVgAgWqXBnxipSCsf3/ZfNoqm1uVxboRUO8i9Ndmjl4pxKOVsDwkHNlt4HrpetHZ2FFm7gG8pzm&#43;0M9VY7sKfRaHxyjVYtO8K7q/1I6AaXQ0SiV&#43;vFwUK1GiH5DCHXriZ2BWp42gGBmmBkzk2&#43;QiI3IYIxfAJhdqANL0S6Hsbigp4zXNrqnKogUdHj7aEXh71n4G3iY51do&#43;OHr5sKj7U&#43;QV8f7&#43;8&#43;MsrFutf7N318cEbUa0HKplQHrxm65uEsmvr871e/1i1cdOzn/3lM/8jUeqXv/Db7732V4nztY9t&#43;LzT6eY5gvtCcW9923ggULlhaodnJCJdLCVGGwe3dwAc5WPN6VHEGO6C7nq9og5w4uyuABqBKquTCiEci/3AcFOgiO8V2CODmJiEC4uTQ0BcUbjOqijdHgMHnPEmSVIVJbI9cXSJgBtrLZoJ7jWzjem3qtrpf4tqDAHNvnLs87vk6TzPj&#43;viH8uHembny/T2fz36JSHEiNBwnYtwnzKRpLRMSmfwXBYSqCoe0rPloUQLD3TBZYxhi6soy72iorufaOP6Q1&#43;MlhSt5wDWzyjs3uvTJnHb28XFRm70NwZgbNQbV3W02gEfV9GMsjg04dGVGpnbRmlnzPLBgz/UzIfOQusX/SMfSul4tuPorixWVLVrckxIMnxd16QZTdPmRezeZtzARQvGRhYuZohTVNWJ4YSjGBdjLOv1TeNNzxphgFCjzlVrmE6jMbfbzQhcbHBH/7AQU3jbMyPNfN4YUywW4CLX0OwbFpcoJuVeXWw85PCDbgOdtMMyqlVsss/cvH3BlpSML4yvFqoMRxF8nWUlJfREZ4s6sp/uLKv5ETl&#43;hd/83OHXulB&#43;06O5LHtrrdmHLdQceCfoB2OY2005GuMM4v1weZkRkuDkDUna4Iv54pmTUd6BeNS7wG5SCsQMAoVL42cLD31nQq3lgAjnnVRK6eFxI3yFGiNC1mdAFhzeQQliKLUi2lRUwwYOjzXpdogFijRHvCmxUhgpq4yhAjio&#43;7qoQcVEuSiIEAzQSxQkAQ0Sx4Yplgxt24Z5d6i8eHh&#43;8Q324nVss/apzoefF7c8Ka6gjLMsK43RVU28mTs3USpdHe47evV4e5vD7sUIichnUlcLoZoABX1d2siU7&#43;tGv&#43;VGpB4XZQZsGweNLmzLSdRMRgWvEBo9NQ50YUJo27h0ea8AS9iJeYIhmjVFAQsXJnF97z9yFYhkgsMLaD4ZC&#43;PZbZATlknS6Qxg2MNpOGku2xoUs3Gu7gkTcZ7fCg&#43;19hQwjj1Y7GubPXHP7x5NAjFCuq5RUYhzXnDvm74PGhlGVTzX2KNSqnehWjZ1KcMimzZWq4AiYcZaoD1bgkObGD/nQGZAo1Y05cPTooJGgQdB/wQBrYDSK6azdgPjlsTvX85zPJRbchGSK3ZpkO0GxmIXYy/yhCQXXPD/j6wvCbVtO6ue1Sr33qd6L7w/FX/&#43;/BEsIBpFREQEO4LpqKDR9BTEYEQRREUUbdgxEiNiGoqkKbYkqCSYhggKwRCiRjCNlOblJb573z33FHuves4p3xhzzbVfPAkX7n3n7LOK&#43;dXjG6PFaLtqXsjuav/k2j1xhxdfuLl5q7LmTePXax3MEzOr4mPvfH/f9/03/vZH&#43;s996fLb/&#43;5N76Xb4F2ZBEaLCY/F3WXgsZaKC4A68zbS93ZdR6&#43;TaNw4TtBaHdqNu0DZHM36&#43;ztJuor0DvIQvAY4hYp&#43;cThpKgYQCreu4BUK14NIvm/AqACYJ4WhiTmjAp0BK1gA5GDGenfZlIsxlBQz64tUSr0ByhVEsqoQuSYuHt33OXnjvX7Pk0/&#43;6CsfDzYqW/zbS9/96esferJ7i8Q6fE&#43;536N&#43;Pp6OxxK5w/393dPHVxy6ROFMONNKcmEUdPTYvDlX0mgOe/Z&#43;U/tjLSOLbibzhlgglQQimZ&#43;wuEZ&#43;T4edZ3Y06uskf8Hwi7fJJj999LnYmjHm1a99jU5Ng3et3O1Ialu&#43;&#43;S2Z2ilM8/F4HHsIzV/tjbVF2&#43;YMZQk&#43;vq7zlCKzwdMYhiEXigmGgO&#43;aoRedF9ezxOzFzcX5Q5OXhSfBfQz&#43;0mWFaoUQis7nfk1OqbTWyzxnlVM2BflgT0PPQV3mpkwb&#43;GfrVokzBHhB7RPLwrQqDTL89MyY4rY&#43;nbySeeHmHGiCUJLyH6Kxj8OgqBuE5kH71G&#43;LYI9Pbobb8OrT7vbln/Mf/w7/pd/e/0p0ftL27j//S358uXf2tSXevXb3qvJ&#43;p/pTeaGqkizYZChQ2qtpmrtlTghPx7liQromKim9EQIWhSrEbqi0NN51RALhT4/hhfFKVa5QQXkplxavN&#43;RKW9Yh6Fli7TxFn3qV2SehQe80Jmgw4K9fo9opHKC5SRuDrMtosUi&#43;GrFnSyqM3f1swX1QlqUGUSiXwsbbY6JGQOYKrgvUOdCPUeueg9b6s7vvevfh01&#43;2L3308IPP7KV6Teln/70JrxdRFaWyTrnCtpcqXu92h7p5MaALGrWW8lgbXdW7nTjE8bU7QyiOV34MkjYVYnhhPLFtQKma1/Vy/UoqwDyIG5ZVzeklYp0OaXRqugI8wXWtVJ1xiNGYYT3BnBpFxhOlbrpLQhdA6jSMYz&#43;egGoexpwFgCMwIvSYog91XTbgKWX8HIZh8lPg0qFi8zlKtQQCo&#43;e1SZoGa3MoEbsneQ3MvvAsaW0vv/yyOlO6oRSF0XpGtWS56Ge1tzoEp2I8lvPrMCQr0cUyGrVYLo2sAYP7fDVbCcSZxWlKSl2Oi4f8vYvcc5jFN17V2BzWUt9znuxQcRSFOhPEVKvUqMs&#43;MjN68U32fU8sGNXGMliUDFVpYhaXcRy/pfjiX3a/&#43;ax56dd3vzZExxgVY9zJt&#43;5jH1XTtO/4/293p4988r1/8/9&#43;5s/f8QvTNN199auqru3NTV3XaVcDqfteOVKxSIaAuMd0rrm4yF04Chz7ZVZKtU2bJB1QXYhjC5t4X1K&#43;L8H2CfGx8Px&#43;U5HLKzsEcuLA8vPlsbAOryqMoDbdOo4KkzzCgsjMbWzgIarKcC2m7zt&#43;grPi6fvTIyOwIhg9ye6a8uoib7rwsqdF/&#43;kbfvqVsDtvrmwR8g03BjijYRjU1HtbPY27aZrI38&#43;NlHHmupy4vOui5eJbVgBYsfhxCyBmq8zLps68U0ZtJdWcVmTkV3C5PPHgAvZIgghaV&#43;y7kLxb6atar4ylCVv6/DHhw3PrFHy8ExJ1DTLVOEwQkZP/Ok/DfK8e7f8CYCWO8VTdrqWKFWMgSllr77LoBN4jG2N4qEnybl705UVuMuVgrrW&#43;vLzMhWg4I34r12YNWCZ9JgncvfSS1IM4qxGpqwdw9dC0ef2QToeza6qXUCOa6T4BKgZLjgpLY6v7S7oT6J9LNpz3YaDW9sHP8yyrc3JTQsN4sstSLA3XHbzfRZNTtd/7zO&#43;&#43;&#43;&#43;k/6kp/5vpd73vb74y2UtZ&#43;7gvvnkrzgZd&#43;2fvlO0//&#43;mMPf/&#43;p4l2fcD/wE8s/vHP6XAjhz&#43;qf&#43;tDFz9qiTBwFITh5hZWfl7HvVOXlWbsyUcBL3WI2vi469WIVyPZePQ6mLHcACY790Pe9066u6wHbVBFRNNoNZNMfSNDHzrbOB8JATDyVQ2QA5oGrkAi0bXk41LhmlhWetRUYhTBl1VPwcZ6Lu&#43;F1hgolRGNMDSwOTdqozSaHuEASvNntxGK7ruuhELuQcn09izoL0CFR5Cj/Znh&#43;L8&#43;L&#43;aDL7Y2JsR1BMjnEVZecODzvFwt0ceS8FLAK8si1ZSJSl5pAS&#43;3qajGwDqkgpaiT/7OJUprGnOXp2Buj97fWii/ruoRgsfbAMb9WVG/0PhHwNU2zpZo&#43;EQBIShzn7b07m/fac9qYYw/vepn7hG0GYe3ZqfaqrCwgQxbbVLu6qetavXpPihK&#43;03mePDtk8KrcTOaiH75tYlmHBMRowlFKl&#43;vVxD0CLPTYD5KEXlbspVGYXp7PSr3E1ULeTlmWkNSow&#43;SJFxgg2J0LAWOTNGTulYA7eNHNXzwhZ1LWy09bO8&#43;eqSxYHDeWQ2UKVvyFnz72zz95FfsvXL3t/d//kaHcS5EwDZ/69x8eS/sbb/19ceBRvQX/7qmkCg802Pazl993e3eHRoW4bTVnoSd9upK3jpw3kIFhGsZJ0oG1R4IF&#43;ozjvSiah/uH46PEN6sRZ&#43;ZEkbupQDib9yVPuxC&#43;yYC5JoZZdFJ8Y48eNz2XJtOLKR8IoJPrHHrWTHLljRxxQk3CK8&#43;2eZ0POZqVq2A6W2J&#43;nlIMv7pMTCuZo7esLASr0plwLitoKaVee/aM&#43;zQ8KDHGAvxPKynaAv7&#43;Od2d1rqftzIhJ36SmzquHGpjXF1Tdnie5/7hoSiruq6dc0FFOUzzpJb5hTe&#43;MbFPzEtQsSiKErVrN/RZE4u3kLtZPNaZ1J5mduhVFhafYPwbaHntQVheLBzX/oXLrL/DQS3/ut/vz/vnkiOgOJxtcvFyTtAWCngdfd&#43;LlfYDyINi3ig6uAO1SLFxYCgAa62bPRqWCAAzWhcxidTqlPqyl76yfzeHCzKfkpebY0s5A4VPE/6qVph9RrCF&#43;CQoHze2ACjsFFWdej2ZhYu3aaG2kasb&#43;UfI6L/5g19fPe7CR5mB2tlnJMUAkOc&#43;3W8cud/6H594z1//1off91evXv9fdMaLa/P4kQ&#43;/3bTqPT//9HTyfd&#43;fnt7msY0p08DAOSdZXymfLi&#43;4l3q9xrqi2zX5wJUYBc3QfZ9Xxgbu8WRy&#43;edxyrRppIYz2KEYOoC/QeeuC1eUaYHu&#43;u3XK4glMY0kpAr3SygEuVCWWg7lYYhMEZVSw/H08PAgWeI6&#43;g8qGudKxCiqy9EBkfEDLiOpRs&#43;jRNfj/cN0gnSAc7YSA2Akp5Wywcghft/32zIq32Vac3cqSxDyABvJ0ZfUbY0pn/I&#43;8VQ35dZkNgm2Ya31JDdUaZhpnAv4Fe2g82w2csxTy43cn47igt22acyfvfIuy/8z8PJeaLesvDZ8gvisSNkAuVmKnuTdqY1vnB1g6gkNW7K9toXlr9O81T7WZcWJw6PPORcbeExWuxHsHNPCQSOhwXAiYzKPDLnB76rQFDwf&#43;PFr0fPWQHVnsuDDkOiKoKSVVv6M2XU&#43;N65mFbbsLJNyrl6VeVkWgjNnX/LvcIKJX57rJQQRqV/8p/R22RvMg8q&#43;p85t4ovNLrzG4gHvNoTr2689txdyIqG/ej3dfvSTP/6Z//O9v/ptH0qNX1elgyKZfaL/0mAw4twPtCAqMx4Ny7Tq6BqIB1ellVjxeHefx6pz8JndyzfOlGULek6J1dNkQ3I3bPJlMCAj2O1wm0wiR2n&#43;f3/YSPYIYsH43nUQ5hnBoD&#43;MLO3k/2wwUP/Brep&#43;IaidSZCYlVk/4YHbViUxfM274LTTIG6fD1r51bZtThTTOAHnwD15ZC2Dpyc&#43;xFGuMlWDaGcgunJmTr2CVWs/HV/yVOeklDV/13XLMFxNNiOZZjgFdrAdZKwNJGPZguqnMS7Ljary9lJu1Sqlrq6u8q4f74J/JTkO55lhBVRqrdv9GeSDDDCI4t3ebQQmaxkVY7w6XLDLDQKjOTXAl6V5PlJhUC7p3N3AGXEPiVtBNbq/S2VzOXA&#43;T52QVJ//SxIquJDnxpCgKwwr0Eyt69ICrTuO4Xh3f3d3Fx/hqR/GtCzhnAHNMKsh4gjp7ypib5Mnw5P3S9574bcV69jCe9&#43;Nw0zJ6xB0/f5/yRcX15&#43;XOq1wORVkSRJzbbx&#43;2bN1DfJLKR/c3I&#43;mzJ/Z1elgseed0gapLWvMS5F30TmQebCKGwg&#43;clGzsM75fkiOZlXZFrMxxmF6p&#43;DmC6TAKI5DXAAiOuOmoBJPbU0eGFC6jb9reDxmVX5OIPk1mXmbS8PHWWXiWTeI0nAqi9mv9IXf9DVPE7fkHKzLL5Ch8d61ZZZrzSO&#43;bAbGGGqgsxizlGJdI15qmQCcECz26SBKoqGrzU5BM&#43;HeJ7HP6dhN06SXwIYwucWNMbNfxmGcGeGnfosMVJyrK455sYw&#43;JZE6tY5Jxzk5dBCpZjeUBWhzCs2jVcFlsG6kAQe0g2e8HtL6JAJ3XEa72Kw7z/kI5/P97XMeLO5&#43;Zd9X8o1bcWQePA7eJoglakfNRUK5EiOJ1ZPG5/ZkcsqctsCBZseRV/8uHuYsvD5opAwEqD48qKpSdSMndva5A7Lf7RlyMPcl8hlrNuOUkmexFHkavIH24pC74mH15xwNZfmIpK6Gz9TNL30qh/h4NhKcfFoMBk5VXiShixYHNH3u6hrlPI2TgSbqOd2EGMZBkopzpSWvIj5ZsoiSYk3D5JelMq6qquOhoKoNOr3isw3YktjT21rl6P7JzZx6ye0NtljIGwzWwspVRGKxdvJkAZfXlhwt6V1zrctjkR6Y3&#43;6rKwI6OfI/coYtvaT05OVcd8eiWuEiywoG1mlHbyWXQ4dZ7ATfAPp4Md05LjVKUKbQy7JwsYG5tJRea&#43;6TkqMzT8y5NKOlwgZSQARm5KHefDnFtC5Cdwm1BFb7uVwSfz&#43;n1dPRrCkJ&#43;nNt2&#43;4O&#43;6Zp0gLmmK7NGEOfctnsMlVtFgRhfsTTht7smc4AeuPkkU4JvIWnGIeEjsZp3Zqpodiaz3zz6M7dXF/LBdPprwm8Z5WoFDHPNGA&#43;jYnKCeTlZoUO&#43;5gv7cYEQjgAE/KcchK/uWZqh8kyNwEicF2ElAxOaktKn2rQ2RY4wyGRKIAlmlqNKLUW7Egt6EinSTuO3sPpCPlbHGq3Oa8CUgx0iMnFIz/S6o8&#43;T4C1ZAN1Vdc1EU6n00nOXADmg/GNfcsh5CQwUBAkaUlCnX2cuEugqsrsdnVdT8FjLxemUonLp1Jhd/8o6R8eosHaF5sxE/IkZ9CsCmocxwA5j4DdlNcN6HmeX9gdDoe6rPq&#43;f3x&#43;1x&#43;PapiTju46&#43;2V9kWqVymXS3XO8V9m0eWxjzgIoN0vGrp&#43;ldl1UWdZFxYk59PVQ4XDouPZg84J4QnoTOovolIzZ6Jwuqhrdfja9jVFNUyAq5lZ/jkVp2vF4FB9PAVHqSnMkU&#43;LY1dCCYJ8zLdcsqSSBzxNnRJDpOC/TRDcqn5Djj0qgGnGO8zL0veq5VFSb9YAms8HX1MS0EbFq9rHnRooMLqMzCPMslsO4rXky9UITqL26YJ66UkaHFW5N&#43;GqSsw1UHjzL0SRJIYJCcda6cLItRlJJwAgooMq2ISBHwe6wSyRxclc2xMYlOWUAiqFcNWdYbkqhYyoEmEFIjdZUdVPbRpzh87suJGkErxFCqKrdYYeZWZLHS5csZlkkVpORW5684vRb3ufVPgeqjQSLA7MzKqK8D6zVH38x7ytyqOBjanyVVVXWVYxxhMXzjIbep4OFBUC3frFnaBJIcMnLyq6W48gYGJyBSr3mTT4&#43;PqpTL3E4YJtnEB9pLvZg3JdctNJiPBGmWyDGMhnjb6QBd3pM2ypa13XTtq0NGioUYzYAwzMF6sDZqnw4TNjGFVTrj5mc&#43;azxXu/3e5i3h7J&#43;kGRTrjCNgow8&#43;fyayeRwTuPAJkoqscLatsn1dhSnwM0StZbu5BNN7eIVYMPkwMKn5K0XkD04rF7I4eg8Dkdhq/3&#43;cH11OBTeikedumkcx6RsgD/bohqGISy&#43;bdu6bbjrN89ziVLIS0WZppoFAcXjLFEXhp3iDMEJL13QcyUqRlBDpaRUYojLd8EC4YpZDAn3FGSTkdjVh51ep2XnazfLggEV&#43;iDUZ0jxTbOanYGQC3lbjieW7Te1AwtnJVnhk9tn4j0xp4jDJN&#43;JQHdR1KCwjZzckK3Fe19wbBO2JJYVJl/rGJY4L0mVktnExSGDNxxn2kQltBIOKT1ryDINDDFdKosFC4PXGKj1ZtXHQp4mEZUqhGWRu/EecRgkW5NWf/INuY1KvrMAh/WxP8rLszqxOoRgF5CABGBlAZxg2unO55nTyFciaQn0iaOTlD&#43;Ssy91O8ley6JYkquph9ZLQM&#43;hqKhgaOq6CnocR7Msm&#43;B4GNNopCyxZOXaQj7s&#43;DAnmXMudgH/TMeBcwE&#43;tKrIdJ5H1WfAA9sqdAqsBgPOMcHuzGzDsUNaOyIXgC&#43;MxAhroGqAHyrFQ0ABzu&#43;LSxgtq1PQlwIh1ACbrUGkEuVilwimiqGSrHiPPZ46mkwXfpwGeVVqY&#43;ivUSnFeZDYgux/QnyLE/daxapdYKfMGms8lemnTuXIhqU8g2xrnEYnhaslu64iY6PWjWrE7xgpYhGqta3EK11d7qc5zN0gtXQHLDG6/ctp3PYcMNlV0adjvSyK3QHxKVKDLMtS7g8YFwGcAP62iL40JbbZIGbwosVUV5eSZI5iDeWyIZwVBOUmG3LEpjRM4RBRYWlqjnlr1yoDPMmydVKQitdViwiJbRaNLA/7wDGl/YZqrmD7B5d4A3WLGSsKNgnZG2OOXZ8F0ApbgGgWq&#43;D33TRNp6VPmgxyDrH8QF6OOax9p7DAdipVcN01UHMopkSq1PLLigrUF&#43;DNmgvK4vzhV8h3JakIZyhRbsO1NawTYOsAgg4s1D48HjMgwZ2lmgxYM/bPPNvraFk14EaKLFEWji4kIY9dh9QdKnK2JNxPbuD6Sqxr8l3XBfB1zeh5BjSVk4Y62AzUPIFufp/LRUly0s6zeewxRiLJ6EbyplSVtiNtUaT9VVQ&#43;tijqRkxWDIOb9&#43;JZQoPHDfFHazV1A8Sd3T2/k9&#43;lGFp9FrnSvoLDhge1wRWFwY8Opw7pGdYVPJfR5RB3M1JiBfPzKUkDkUpQq9LZWozh5IXZIlWuqkphWsvdl/H5KQAjKjeFCAm6mli2iRoGm09pqFOW5f7iwAVDrtQzW4gx7lSzLMsUZpSiSL9d0EWRcgcSwQGKUhp5a5f1Pm8pzWgHe0/oBQ4odKE8&#43;AwKyLst2Ao0UNSiYVBE6PF0TNeslC4NNR&#43;dc68dj/JUJ8n4CuCoUr8GTMyhMuwviAcfMVrv14zGWmcRlrhLBAOe/MIhFrIhDdUO&#43;CFMjymmSMeRpIBxNAzAS7zOu9OtHDayWBmb6/kac2DWqHRJDNd1gNtF1TWpMA2DejypcXRVKyUkW62K7gOtmRkPk6ZrtslgYVLcw39Fy43Xqf7gy8wMxDdjnM1tnlhjt9NhmKkk9OseQhJgGCZEwZ6Rlc04GQFeYcGfHv77xcsbdopQFoJGiAKZhNFw9c9LrTuIyUz2Yl&#43;WZRXFzxUgx9ToGz8ufZbb0rOYt&#43;97eXNLAkjwcZ&#43;TIBIUSXQlh0nodk6ZBzs9bjS0ume3rOU0VGdUFhkrjSrg&#43;qSic6hdg1980zbsDUMUA0rqWj5nGliGoOXmAmbp8gpfuGokex0kVZtOyH9AejpB/qP2SJuXdWtyWTjDjGjUkVbBoru&#43;K21SJFZqYugDGGJnKiDbgN9iskdg&#43;9ylzirx5OxQFAX7n6qwqqosRkScFBQjaFbDjA4I1bSCZMLrpB0ptDi1Usu9n44d64gYotdkApDvbHY1ykVF6gXwF7ppmvbVfpqmhSCsGRQIyBqqtkHmwsIeDZcSo06MGwsJeFsExl/kEMXaZv7KiK5Q4SB3CjCpH5YEp1mWm5sXswErXC2VdVRq6QBo5EKOxsMwpEGj1mpBi0sbqRgb9GgN4Sg2TbNjVPePa6cNW3FlmbbrT6Ocq7ZwVWWbisMeOXj3j3KjCxs6MTvTi92FnB&#43;qqeONkFhihA4Ds0VfQmYQfWutPvAV5RKwuoABI8sLM1u0IBIxMKdwJH&#43;nyQbDzq1epw5ybXjoSwEIODkYXrvFyNuCQRT7uiZYa6lUxBarJUma5yh/Fve5xARUIhIiBLXDNWJ0JHGAMw&#43;xxT0BGBm7yx7UyBfAh2uRuhCxPHZpeGuw99cPaaretipLzGiMTzi2cetAi8qE3iteJ0TelGMd65VzRVuLu4mQvSQPl5pU5n159VUkbxj0u7ao66Zqy7LsDBq2k7iSbMDyowToARpGGReFA2q57o9DNjPZ4JgXe6cGIyLizjifDJb6L&#43;L5IkokLqNG0HHNKkhGU5WpF70s8RFV1qr4Dvi1nAopdtbWkUVEgoZ4HPoxYfecVVYndTZjXGkJvmByJJGwdOM4zh0wiZPnx0tkww9VLYgNcELA6rNMy&#43;izZjWLF/JyMBdwSINdUJlXhJpP0yaraxGBS1Db9RihhW9KoYGKyBkkDZgp9B5cWalVNqOIQzSODhG7kGdsHLp0iJxV2VDfSH4Luv2EFSmQAgZF1jGLQ4Uh&#43;DjLxyy0IHnC3qjgwwRQEz&#43;TSyYpTM5pJGGds/umruu5kLfwPwEAAP//3CWOHExe6Q0AAAAASUVORK5CYII="
style="width:100%"><input type="hidden" id="antivalue"
value=""></div>
<div style="margin-top: 1vh;display: flex;flex-direction: row;justify-content: space-between;">
<img style="argin-left: 8pt;width: 25pt;height: 25pt;float: left;cursor: hand;"
onclick="antiReload()" src="/antiRes/images/flush.png">
<div>
<button style="background-color: #24C0D7;text-align: center;vertical-align: middle;touch-action: manipulation;cursor: pointer;background-image: none;border: 1px solid transparent;white-space: nowrap;padding: 8px 12px;font-size: 14px;line-height: 1.42857143;border-radius: 4px;-webkit-user-select: none;-moz-user-select: none;-ms-user-select: none;user-select: none;color: #FFFFFF;position: relative;outline-width: 0px;box-shadow: none !important;"
onclick="antiReload(1);">确定
</button>
</div>
</div>
</div>
</div>
</div>
</div>
</div>
<img src="/images/pc_6.png" class="backTop" id="backTop">

<script>

function antiAdd(event, obj) {
if (obj.parentNode.querySelectorAll(".imgs").length < 3) {
var offsetX = event.pageX - (obj.getBoundingClientRect().left + document.body.scrollLeft);
var offsetY = event.pageY - (obj.getBoundingClientRect().top + document.body.scrollTop);
var offx = parseInt(offsetX);
var offy = parseInt(offsetY);
var icon = "<img onclick='antiRemove(this)' class='imgs' src='/antiRes/images/hoverclick.png' "
+ "style='position:absolute;top:" + (offsetY - 8) + "px;left:" + (offsetX - 8) + "px;' offx=" + offx + " offy=" + offy + " />";
obj.parentNode.innerHTML += icon
document.querySelector("#antivalue").value += (";" + offx + "," + offy)
}
}


function antiRemove(obj) {
var offx = obj.getAttribute("offx");
var offy = obj.getAttribute("offy");
document.querySelector("#antivalue").value = document.querySelector("#antivalue").value.replace((";" + offx + "," + offy), "");
obj.parentNode.removeChild(obj);
}


function antiReload(flag) {
if (flag === 1) {
var param = {};
param["antiVerifyCheck"] = document.querySelector("#antivalue").value.substr(1);
param["imgw"] = $("#antiimg").width();
$.ajax({
type: "POST",
url: window.location.href,
dataType: "json",
data: param,
headers: {
'app': 'jyweb',
},
success: function (res) {
window.location.reload()
}
});
} else {
window.location.reload();
}
}

</script>
</body>
</html>
    """

    captor_data = {
        '_id': '',
        'cookies': '',
        'final_res': html
    }
    data = json.dumps(captor_data)
    captor(data)

if __name__ == '__main__':


    # test_captor()


    # keep_date('')

    data0 = json.dumps({
        'keyword': '心理服务站建设项目',
        # 'keyword': '揭阳市榕城区卢前小学计算机设备维修和保养服务服务采购',
        'page': 1,
        'area': ''
    })
    # search_require(data0)
    search(data0)
    # search_keyword(data0)
    # search(data0)
    # print(get_zero_time())
    # res = rds_206_11.sismember('jianyu:crawled_id', 'ABCY1xGYS4%2FLyg4GWN1cE8sDzMoFjRmYXxzKDg0Ni4wUX5wHCdUCaY%3D')
    # if res:
    #     print('you')
    # else:
    #     print('mei')
    # print(in_limit('2023-01-31'))
    item = {
        'url':'https://www.jianyu360.cn/article/content/ABCY1xGYS4%2FLyg4GWN1cE8sDzMoFjRmYXxzKDg0Ni4wUX5wHCdUCaY%3D.html'
    }
    # save_crawled_id(item)

    # res = rds_206_11.sadd('jianyu:in_quee', '111')
    # print(type(res))


    data1 = [
        {'_id': 'ABCY1xGYz0vIys4JGt1cE8sDzMoFjRmYXxzKz8CPT0eVmlzdCdUCdg%3D', 'area': '北京', 'city': '北京市',
         'publishtime': 1673940925, 'title': '北京银行数字化转型9号工程-“京客图谱”项目单一来源采购公示', 'subtype': '单一',
         'site': '中国中化集团有限公司商务电子招投标平台'},
        {'_id': 'ABCY1xGYz0vJD07EnN1cE8sDzMoFjRmYXxzKz8CPSE3aGlzdl5UCiw%3D', 'area': '福建', 'city': '厦门市',
         'publishtime': 1673940800, 'title': '厦门万翔-（公开招标）-XM2022-TZ0738厦门市电子证照共享库管理平台升级及可信文件管理子系统结果公示', 'subtype': '成交',
         'site': '厦门招投标网'},
        {'_id': 'ABCY1xGYz0vJD07An93cFxbCzMCEjJ3XGB1KDgFIyEgcFVzfj9UCc0%3D', 'area': '辽宁', 'city': '大连市',
         'publishtime': 1673940760, 'title': '【长海县】【单一来源公示】“智慧平安海岛”租赁视频、Ais及雷达数据项目单一来源公示', 'subtype': '单一',
         'site': '北京隆道网络科技有限公司'},
        {'_id': 'ABCY1xGYz0vJDwsRHt3cFxbCzMCEjJ3XGB1KDgFIyFFWlFzZD9UCew%3D', 'area': '四川', 'city': '成都市',
         'publishtime': 1673940495, 'title': '成都崇州大数据国家新型工业示范园区建设项目—配套生活服务用房（数智林盘）工程施工/标段合同公告', 'subtype': '合同',
         'site': '成都市公共资源交易服务中心'},
        {'_id': 'ABCY1xGYz0vJD06GXt1cE8sDzMoFjRmYXxzKz8CPS8ecGdzfjNUChI%3D', 'area': '福建', 'city': '厦门市',
         'publishtime': 1673940373, 'title': '厦门中实-公开招标-2022-ZS2566-“互联网+监管”系统建设项目-中标结果公示', 'subtype': '成交',
         'site': '中国政府采购网'},
        {'_id': 'ABCY1xGYz0vJDwvAnt3cFxbCzMCEjJ3XGB1KDgFIyENZGhzfCdUCZY%3D', 'area': '福建', 'city': '厦门市',
         'publishtime': 1673940348, 'title': '厦门中实-公开招标-2022-ZS2565-市监优化营商环境配套项目（2022）-中标结果公示', 'subtype': '成交',
         'site': '中国政府采购网'}

    ]

    data2 = {'_id': 'ABCY1xGYz0vIys4JGt1cE8sDzMoFjRmYXxzKz8CPT0eVmlzdCdUCdg%3D', 'area': '北京', 'city': '北京市',
         'publishtime': 1673940925, 'title': '北京银行数字化转型9号工程-“京客图谱”项目单一来源采购公示', 'subtype': '单一',
         'site': '中国中化集团有限公司商务电子招投标平台'}

    data2 =  {'_id': 'ABCY1xFdTIFAjYvRGd3cFxbCzMCEjJ3XGB1KT87LyE3fFFzbwVUCb4%3D', 'area': '云南', 'city': '红河哈尼族彝族自治州',
              'publishtime': 1678781541, 'title': '关于为【蒙自市雨过铺中心学校】公开选取【工程监理】机构的公告', 'subtype': '竞价',
              'site': '云南省投资审批中介超市'}
    data2 = {'_id': 'ABCY1xGYD0eIyw7NFF6Z3UvJjIoFRFjXGh1Pw44PTogXmlzfiNUCeE%3D', 'area': '浙江', 'city': '绍兴市', 'publishtime': 1677053572, 'title': '耀华建设管理有限公司关于绍兴市疾病预防控制中心公共卫生>信息化系统维护及结核病信息维护项目单一来源采购的公示', 'subtype': '单一', 'site': '浙江政府采购网'}

    # require_detail(json.dumps(data2))

    data3 = {'_id': 'ABCY1xGYz0vIys4JGt1cE8sDzMoFjRmYXxzKz8CPT0eVmlzdCdUCdg%3D', 'area': '北京', 'city': '北京市', 'publishtime': 1673940925, 'title': '北京银行数字化转型9号工程-“京客图谱”项目单一来源采购公示', 'subtype': '单一', 'site': '中国中化集团有限公司商务电子招投标平台', 'orign_link': 'http://e.sinochemitc.com/cms/channel/ywgg1hw/124978.htm', 'bid_detail': '<div id="tab1">\n\t\t\t\t\t<div class="com-detail">\n\t\t\t\t\t\t1. 项目名称：北京银行数字化转型9号工程-“京客图谱”项目<br>2. 采购人名称：北京银行股份有限公司<br>3. 采购人地址：北京市东城区和平里东街1号<br>4. 本项目资金来源：企业自筹资金<br>5. 本次采购内容为：本项目是需要供应商通过大数据平台对商机数据进行加工处理。<br>6. 拟采购方式：单一来源<br>7. 拟采购供应商名称：北京东方国信科技股份有限公司<br>8. 拟采购供应商地址：北京市朝阳区创达三路1号院1号楼7层101<br>9. 论证专家成员：<br><table border="1"><tbody><tr><td>序号<br></td><td>姓名<br></td><td>职称<br></td></tr><tr><td>1<br></td><td>张爱恭<br></td><td>高级工程师<br></td></tr><tr><td>2<br></td><td>赵刚<br></td><td>高级工程师<br></td></tr><tr><td>3<br></td><td>杨宁<br></td><td>高级工程师<br></td></tr></tbody></table><br>10. 论证专家意见：<br>中化商务有限公司于2023年1月17日在北京复兴门外大街A2号西城金茂中心组织了相关专家对该项目需求文件及建议采购方式进行了论证。<br>经论证，专家组成员一致认为该项目需求文件完整，单一来源理由充分。<br>11. 公示期：2023年1月17日至2023年1月29日，共计5个工作日。潜在供应商对公示内容有异议的，请于公示期内将书面意见反馈至中化商务有限公司，书面文件包括：<br>? 有效的营业执照或事业单位法人证明复印件；<br>? 法定代表人授权书（如由授权代理人提出异议的）；<br>? 异议单位情况介绍（包括但不限于供应商名称、联系人、联系电话、联系邮箱等）；异议说明、能够完成本项目的声明及证明材料。<br>以上内容均需加盖公章。<br>代理机构：中化商务有限公司<br>地    址：北京复兴门外大街A2号西城金茂中心（邮编：100045）<br>业务联系人：唐昱<br>电    话：18310298572<br>传    真：010-59369323<br>电子邮箱：tangyu10@sinochem.com\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t'}

    # data_clean(json.dumps(data3))

    data4 = {'uuid': 'c61688a3c30ea93ea7d06e5d645235cc', 'title': '北京银行数字化转型9号工程-“京客图谱”项目单一来源采购公示', 'notice_type': 1, 'bid_type': '单一公告', 'pub_province': '北京市', 'pub_city': '北京市', 'pub_time': '2023-01-17', 'money': '', 'notice_detail': '<div id="tab1">\n\t\t\t\t\t<div class="com-detail">\n\t\t\t\t\t\t1. 项目名称：北京银行数字化转型9号工程-“京客图谱”项目<br>2. 采购人名称：北京银行股份有限公司<br>3. 采购人地址：北京市东城区和平里东街1号<br>4. 本项目资金来源：企业自筹资金<br>5. 本次采购内容为：本项目是需要供应商通过大数据平台对商机数据进行加工处理。<br>6. 拟采购方式：单一来源<br>7. 拟采购供应商名称：北京东方国信科技股份有限公司<br>8. 拟采购供应商地址：北京市朝阳区创达三路1号院1号楼7层101<br>9. 论证专家成员：<br><table border="1"><tbody><tr><td>序号<br></td><td>姓名<br></td><td>职称<br></td></tr><tr><td>1<br></td><td>张爱恭<br></td><td>高级工程师<br></td></tr><tr><td>2<br></td><td>赵刚<br></td><td>高级工程师<br></td></tr><tr><td>3<br></td><td>杨宁<br></td><td>高级工程师<br></td></tr></tbody></table><br>10. 论证专家意见：<br>中化商务有限公司于2023年1月17日在北京复兴门外大街A2号西城金茂中心组织了相关专家对该项目需求文件及建议采购方式进行了论证。<br>经论证，专家组成员一致认为该项目需求文件完整，单一来源理由充分。<br>11. 公示期：2023年1月17日至2023年1月29日，共计5个工作日。潜在供应商对公示内容有异议的，请于公示期内将书面意见反馈至中化商务有限公司，书面文件包括：<br>? 有效的营业执照或事业单位法人证明复印件；<br>? 法定代表人授权书（如由授权代理人提出异议的）；<br>? 异议单位情况介绍（包括但不限于供应商名称、联系人、联系电话、联系邮箱等）；异议说明、能够完成本项目的声明及证明材料。<br>以上内容均需加盖公章。<br>代理机构：中化商务有限公司<br>地    址：北京复兴门外大街A2号西城金茂中心（邮编：100045）<br>业务联系人：唐昱<br>电    话：18310298572<br>传    真：010-59369323<br>电子邮箱：tangyu10@sinochem.com\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t', 'url': 'http://e.sinochemitc.com/cms/channel/ywgg1hw/124978.htm', 'doc': '', 'source_name': '测试剑鱼', 'other': ''}

    # i = random.randint(1,8)
    # producer = Kafka_producer(KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC, i)
    # print("===========> producer:", producer)
    #
    # producer.sendjsondata(data4)
    # time.sleep(1)

    data5 = {
        'page': 2,
        'count': 49,
        'keyword': '大数据',
    }

    data = {"page": 1,
            "count": 10,
            "date": "2023-05-20_2023-05-20",
            "adcodes": "150600",
            "orgTypes": 4,
            "bidProcesses": 60,
            }
    # zl_search(json.dumps(data))
    # zl_search_keyword(json.dumps(data5))

    # rds_206_11.hincrby('jianyu:source_classify', 'zl_2023-02-10')

    # keep_date(json.dumps(data4))
    # page_data = get_data('weixin_43471909', 1)
    # page_data = search('大数据')
    # clean_data(page_data)
    # print(int(time.time()*1000))
    # kfk.send_message(data4)
    # aa = []
    # print(len(aa))
    # result = MyCsdnDao.get('18987865@1644473472241')
    # print(result)
    #
    # res = rds_206_11.sadd('jianyu:crawled_id', '12345')
    # print(type(res))

    """
docker network create --subnet 172.26.16.0/24 \
--opt com.docker.network.bridge.name=docker_gwbridge \
--opt com.docker.network.bridge.enable_icc=false \
--opt com.docker.network.bridge.enable_ip_masquerade=true \
docker_gwbridge

    https://www.jianyu360.cn/article/content/ABCY1xBfzIeMyYsAmt4dXIkMDBfDSF3V1JxKC8nKj0neGlzeyNUChQ%3D.html
    """