#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : zhiliao.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/2/7 上午9:42
@Desc  : 
"""
import hashlib
import random
import time
import math
import requests
import re
from app.moen_app import moenApp
import json
from sonyflake import SonyFlake
import datetime
from model.rds import rds_206_11, rds_206_06
from common.config import judge_notice_type, single_province
from common.us import UfileOss
import os
# from common.us import upload_us3
test = False
# def get_proxy(cls):
#     num = random.randint(0, 9)
#     # print(num)
#     proxy = list(rds_206_06.hgetall(f'proxy:asy_{str(num)}').keys())[0]
#     # print(proxy)
#     ip = proxy.decode()
#     ip = {
#         'http': 'http://' + ip,
#         'https': 'https://' + ip,
#     }
#     return ip
@moenApp.task(
    name='bid.zhiliao.search',
    bind=True,
    acks_late=True,
    rate_limit='5/m',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def search(self, data):
    data = json.loads(data)
    print(data)
    keyword = data['keyword']
    page = data['page']
    date = data['date']

    phone, userId, token = get_cookies()
    print(phone, userId, token)
    params = {
        'userId': userId,
        'page': page,
        'count': '50',
        'date': date + '_' + date,
        'keyword': keyword,
        # 'searchScope': '1',  # 综合 没有综合这个选项了
        'matchMode': '1',   # 智能匹配
    }
    # proxy = get_proxy('')
    params = deal_params(params)
    headers = deal_headers(token)
    response = requests.get('https://api-service-zhiliao.bailian-ai.com/search/bid', params=params,
                            # proxies=proxy,
                            headers=headers)

    rds_206_11.hincrby('zhiliao:cookies_count', phone)

    response_data = response.json()
    if response_data['code'] != 1:
        pass

    res_data = response_data['data']

    total = res_data['total']
    records = res_data['records']
    for item in records:
        res = {
            'id': item['id'],
            'pubTime': item['pubTime'],
            'titleText': item['titleText'],
            'bidType': item['bidType']
        }
        title = item['titleText']
        pubTime = item['pubTime']
        if not crawled(title, pubTime):
            print('需要爬：', item['id'], title, pubTime)

            moenApp.send_task('bid.zhiliao.detail', args=(json.dumps(res),))
        else:
            print('已经存在：', item['id'], title, pubTime)
    print('total:', total)
    if int(page) == 1:
        max_page = math.ceil(total / 50)

        for i in range(2, max_page):  # 4.24 第三页就要登录

            data['page'] = i
            next_data = json.dumps(data)
            print(next_data)
            moenApp.send_task('bid.zhiliao.search', args=(next_data,))


@moenApp.task(
    name='bid.zhiliao.detail',
    bind=True,
    acks_late=True,
    rate_limit='10/m',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def zhiliao_detail(self, data):

    phone, userId, token = get_cookies()


    cookies = {
        'registered': 'true',
        'token': token,
        'role': '2',
        'userId': str(userId),
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://www.zhiliaobiaoxun.com/search/?key=%E9%AB%98%E6%80%A7%E8%83%BD%E8%AE%A1%E7%AE%97',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    data = json.loads(data)
    id_ = data['id']
    bidType = data['bidType']
    url = f'https://www.zhiliaobiaoxun.com/content/{id_}/b{bidType}'

    params = {
        'clickIndex': '1',
    }
    # proxy = get_proxy('')
    response = requests.get(url, params=params,
                            cookies=cookies,
                            verify=False,
                            # proxies=proxy,
                            headers=headers)
    if

    rds_206_11.hincrby('zhiliao:cookies_count', phone)

    bid_type_tmp = re.findall('subtypeName:"(.*?)",', response.text)
    if bid_type_tmp:
        bid_type = bid_type_tmp[0]
        print(bid_type)
    else:
        bid_type = ''

    sourceUrl_tmp = re.findall('sourceUrl:"(.*?)",', response.text)
    if sourceUrl_tmp:
        a = sourceUrl_tmp[0]
        a.encode()
        a = '"' + a + '"'
        sourceUrl = eval(a)
        print(sourceUrl)

    else:
        sourceUrl = ''

    content_tmp = re.findall('content:"(.*?)",', response.text)
    if content_tmp:
        a = content_tmp[0]
        a.encode()
        a = '"' + a + '"'
        a = eval(a)
        str_content = a.split('<head>')
        content = str_content[0] + "<head>" + '<meta data-n-head="ssr" charset="utf-8">' + str_content[1]
        print(content)

    else:
        content = response.text

    bid_data = {}
    bid_data['publishtime'] = data['pubTime']
    bid_data['title'] = data['titleText']
    bid_data['subtype'] = bid_type
    bid_data['orign_link'] = sourceUrl
    bid_data['bid_detail'] = content
    bid_data['zl_url'] = url
    bid_data['detail_type'] = 'html'

    bid_data['uuid'] = sign(url)

    if 'https://bid.snapshot.qudaobao.com.cn' in content:
        file_url_list = re.findall('"(https://bid\.snapshot\.qudaobao\.com\.cn/.*?)"', content)
        try:
            file_url = file_url_list[0]
            print(file_url)
            bid_data['bid_detail'] = downlond(file_url)
            if '.pdf' in file_url:
                bid_data['detail_type'] = 'pdf'
        except Exception as e:
            print(e)
            content = re.sub('"https://bid\.snapshot\.qudaobao\.com\.cn/.*?"', '""', content)
            bid_data['bid_detail'] = content
        # print(bid_data['bid_detail'])


    bid_data['filepath'] = upload_us3(bid_data)
    del bid_data['detail_type']
    print(bid_data)

    moenApp.send_task('bid.zhiliao.clean', args=(json.dumps(bid_data),))
    redis_key = 'zhiliao:data:' + data['pubTime']
    rds_206_11.hset(redis_key, bid_data['title'], json.dumps(bid_data))
    print('ok')


def upload_us3(item):
    uuid = item['uuid']
    content = item['bid_detail']
    detail_type = item.get('detail_type', 'html')

    ufile = UfileOss()


    if detail_type == 'html':
        file_name = f"{uuid}.html"
        mime_type = 'text/html'
        content = content.encode('utf-8')
    elif detail_type == 'pdf':
        file_name = f"{uuid}.pdf"
        mime_type = 'application/pdf'
        item['bid_detail'] = ''
    elif detail_type == 'image':
        file_name = f"{uuid}.jpeg"
        mime_type = 'image/jpeg'
    else:
        print(f'no notice_type: {item}')
        return

    if test:
        folder_name = "other_test/"
    else:
        folder_name = "other_bid"



    result_file = os.path.join(folder_name, file_name)
    for _ in range(6):
        try:
            ufile.upload_bytesIO(result_file, content, mime_type=mime_type)
            return result_file
        except Exception as e:
            print(e)
            time.sleep(0.05)
    return None


def downlond(pdf_url):

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }
    # 'https://bid.snapshot.qudaobao.com.cn/6637ba012078a3d65e3eda9ba7bb33470d00eead.pdf'
    # proxy = get_proxy('')
    response = requests.get(pdf_url,
                            # proxies=proxy,
                            headers=headers)

    return response.content


@moenApp.task(
    name='bid.zhiliao.clean',
    bind=True,
    acks_late=True,
    rate_limit='30/s',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def data_clean_zhiliao(self, tmp_data):
    data = json.loads(tmp_data)
    item = {}
    detail = data.get('bid_detail')
    uuid = data.get('uuid')
    filepath = data.get('filepath')
    if not detail and not filepath:
        return

    zl_url = data['zl_url']

    item['uuid'] = uuid
    item['title'] = data['title']

    subtype = data.get('subtype')
    if subtype and '公告' not in subtype:
        subtype += '公告'
    notice_type = judge_notice_type(subtype)
    item['notice_type'] = notice_type
    item['bid_type'] = subtype

    pub_time = data.get('publishtime')
    if pub_time:
        item['pub_time'] = pub_time

    item['money'] = ''
    item['notice_detail'] = detail
    href = data.get('orign_link')
    if href:
        item['url'] = href
    else:
        item['url'] = ''
    item['doc'] = ''

    item['source_name'] = '知了'
    item['other'] = zl_url
    item['filepath'] = filepath

    str_data = json.dumps(item)

    print(item)

    moenApp.send_task('bid.jianyu.zoo', args=(str_data,))
    # moenApp.send_task('bid.jianyu.kfk', args=(str_data,))

    item['tender_time'] = 31507200000

    sf = SonyFlake()
    next_id = sf.next_id()

    final_data = {
        "version": 1,
        "trace_sn": str(next_id),
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + time.strftime('%z',
                                                                                                   time.localtime()),
        "data_type": "spider_bid",
        "data": item
    }

    str_data = json.dumps(final_data)
    moenApp.send_task('bid.jianyu.kfk', args=(str_data,))
    print(f'send to kfk: {final_data}')


def crawled(title, date):
    rds_key = 'spider_db:' + date
    res = rds_206_11.sismember(rds_key, title)
    return res


def deal_params(params):
    keyword = params.get('keyword', '')
    random_num = random.randint(200, 400)
    # print(random_num)
    timestamp = str(int(time.time() * 1000 - random_num))
    # print(timestamp)
    hash_ = sign(keyword + timestamp + 'zlbxdc406fce62db4066b1f586677c9')
    # print(hash_)
    params['timestamp'] = timestamp
    params['hash'] = hash_
    return params


def sign(data):
    str_md5 = hashlib.md5(data.encode(encoding='utf-8')).hexdigest()
    return str_md5


def deal_headers(token):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://www.zhiliaobiaoxun.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.zhiliaobiaoxun.com/search/?key=%E9%AB%98%E6%80%A7%E8%83%BD%E8%AE%A1%E7%AE%97',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'auth-token': 'eyJhbGciOiJIUzUxMiIsInppcCI6IkdaSVAifQ.H4sIAAAAAAAAAKtWykwsUbIyNLMwMTQ2MLO00FEqLk1SslIyMjI3s1TSUUqtKIBIGxmaG1ha1AIAizyo2DEAAAA.b4bF73AQtBYke1fUktRagJb6jjyGfqh3yOT_9znjhYYmHiN4700FG-h5CXscpq4nMU9jadVRPDLmoQrbGK2jdA',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }
    headers['auth-token'] = token
    return headers


def get_cookies():
    for i in range(50):
        phone = rds_206_11.rpop('zhiliao:account_spider').decode()
        print(phone)

        number = rds_206_11.hget('zhiliao:cookies_count', phone).decode()
        if int(number) < 1500:
            rds_206_11.lpush('zhiliao:account_spider', phone)
            cookies = json.loads(rds_206_11.hget('zhiliao:token', phone).decode())
            print(cookies)
            return phone, cookies['userId'], cookies['token']
    print('没有cookies了')
    return None, None, None


if __name__ == '__main__':
    a = crawled('伊犁州消防救援支队关于编程开发软件的网上超市采购项目成交公告', '2023-05-17')

    # print(a)

    # data = json.dumps({
    #     'keyword': '宁夏回族自治区商务厅',
    #     'page': 1,
    #     'date': '2023-05-19'
    # })
    #
    # search(data)
    #
    # data1 = json.dumps({
    #     'id': '489133117',
    #     'pubTime': '2023-05-14',
    #     'bidType': 1,
    #     'titleText': '鹤壁职业技术学院超融合高性能计算云平台项目2023年5至6月政府采购意向'
    # })
    #
    # # zhiliao_detail(data1)
    #
    # print(get_proxy(''))
