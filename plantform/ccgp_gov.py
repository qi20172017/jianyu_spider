#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : ccgp_gov.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/7/28 下午2:55
@Desc  : 
"""

import requests
# from curl_cffi import requests
from lxml import etree
from model.rds import rds_206_11
import random
import json


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
    print(f'use: {ip}')
    return ip


def get_list(page):


    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'HMF_CI=5a6bd9ed308ef5ba21d0130085c608f65b22220fd6b595cdd076aa2756043c318729b5d474ec0c0b31ad72dc8d845b6802936347e04f4b164025648c7ca118b965; Hm_lvt_9f8bda7a6bb3d1d7a9c7196bfed609b5=1688721194,1690526742; HMY_JC=4e14b5d4d1478f1c4a495350bfe745668c6a2c8db118b9c98fe656e14aa6cfb75d,; Hm_lvt_9459d8c503dd3c37b526898ff5aacadd=1688721199,1690526747; HBB_HC=7857dd35e74fde396f650dd3328f2db581ab0966d77f1e65e17a54d322d051afdad266dff081641524b6fc34dfa954ca54; Hm_lpvt_9f8bda7a6bb3d1d7a9c7196bfed609b5=1690526773; JSESSIONID=-xibRnAx4-qYhgXm7snIaUkFCIEwkXOb3-9iFBZI-N8KCm6ugfhK!-659060644; Hm_lpvt_9459d8c503dd3c37b526898ff5aacadd=1690527232',
        'Pragma': 'no-cache',
        'Referer': 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=19&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time=2023%3A07%3A25&end_time=2023%3A07%3A28&timeType=1&displayZone=&zoneId=&pppStatus=0&agentName=',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    params = {
        'searchtype': '1',
        'page_index': str(page),
        'bidSort': '0',
        'buyerName': '',
        'projectId': '',
        'pinMu': '0',
        'bidType': '0',
        'dbselect': 'bidx',
        'kw': '',
        'start_time': '2023:08:02',
        'end_time': '2023:08:02',
        'timeType': '1',
        'displayZone': '',
        'zoneId': '',
        'pppStatus': '0',
        'agentName': '',
    }

    response = requests.get('http://search.ccgp.gov.cn/bxsearch', params=params,
                            # cookies=cookies,
                            headers=headers,
                            proxies=get_proxy_ip(''),
                            verify=False)

    # print(response.content.decode())
    x_data = etree.HTML(response.content.decode())
    item_list = x_data.xpath('/html/body/div[5]/div[2]/div/div/div[1]/ul/li')
    for item in item_list:
        title = item.xpath('./a/text()')[0].strip()
        url = item.xpath('./a/@href')[0].strip()
        # tmp_data = item.xpath('./span/text()')[0].strip()

        # print(title, url)

        try:
            detail(url)
        except Exception as e:
            print(e)

def detail(url):


    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'HMF_CI=a23eda9097137327c50ad54f76eded546b5bae37ac522b726c6ce43d11c7f033d21b6324c39006d22ae1304c8a6907c2e6e0b8c0c8e0527d91bca84e81722f3138; Hm_lvt_9f8bda7a6bb3d1d7a9c7196bfed609b5=1688721194,1690526742; HMY_JC=b246e37ad24824d55ec84fcb253c5130a731b3a36d704fb103c80939eba09f214a,; HBB_HC=b2e846377788276e5718b07598b3695098fe2a4ab4fb8233cde98ce786d8da6655a814552009e17d50e9d2dd4ae2402751; Hm_lpvt_9f8bda7a6bb3d1d7a9c7196bfed609b5=1690528813',
        'Pragma': 'no-cache',
        'Referer': 'http://search.ccgp.gov.cn/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    response = requests.get(
        url,
        # 'http://www.ccgp.gov.cn/cggg/dfgg/jzxcs/202307/t20230728_20388897.htm',
        # cookies=cookies,
        proxies=get_proxy_ip(''),
        headers=headers,
        verify=False,
    )
    x_data = etree.HTML(response.content.decode())
    detail_data = x_data.xpath('//*[@id="detail"]/div[2]/div/div[2]/div/div[1]/h2/text()')
    print(detail_data)
    rds_206_11.sadd('bid_test:ccgp_gov', detail_data[0])



def run():
    for i in range(1, 1500):
        print(f'第{i}页')
        try:
            get_list(i)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    run()
    # detail('')