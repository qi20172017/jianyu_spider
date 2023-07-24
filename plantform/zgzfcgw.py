#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : zgzfcgw.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/7/7 下午5:19
@Desc  : 
"""
import random
import time
from curl_cffi import requests
# import requests

def list():

    url = "http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=9&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time=2023%3A06%3A30&end_time=2023%3A07%3A07&timeType=2&displayZone=&zoneId=&pppStatus=0&agentName="

    payload = {}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        # 'Cookie': '__utma=133605329.70330977.1667811068.1667811068.1667811068.1; HMF_CI=794ee9249abf9bd6545c601a982d92da0673d144f531c1cc8348e4e9006411375386be22fb2d0d9bd8ae7a4a3fadcfb66a81d1a9bba47875a3defd472296f75881; Hm_lvt_9f8bda7a6bb3d1d7a9c7196bfed609b5=1686709033,1688721194; Hm_lpvt_9f8bda7a6bb3d1d7a9c7196bfed609b5=1688721194; HMY_JC=648fbccf67c79a5cfc7b3bfb462d0830931932109f8b70280607357083506ee341,; HBB_HC=e0789575e3dc85e0ce0c1cbec2ea9e40326062832e1d996529a522c58b25c55e7361044f7d9c0584e96473d72a5722d199; Hm_lvt_9459d8c503dd3c37b526898ff5aacadd=1686709061,1688721199; JSESSIONID=quovoOXOdp0SPKokryfGWp_5_Xbc5Zotl327-hnmKKKAZbEKUYaQ!-522671212; Hm_lpvt_9459d8c503dd3c37b526898ff5aacadd=1688721221',
        'Pragma': 'no-cache',
        'Proxy-Connection': 'keep-alive',
        'Referer': 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=8&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time=2023%3A06%3A30&end_time=2023%3A07%3A07&timeType=2&displayZone=&zoneId=&pppStatus=0&agentName=',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


if __name__ == '__main__':

    # for i in range(1000):

    list()
        # time.sleep(random.uniform(1))