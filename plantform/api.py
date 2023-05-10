#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : api.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/4/20 上午10:43
@Desc  : 
"""
import random
import time

import requests
from model.rds import rds_206_11

class Jianyu:
    def __init__(self):
        self.cookies = {
            'SESSIONID': '14584c6968b48f1519d251085ab0700deef07b32',
            'SESSIONID': '14584c6968b48f1519d251085ab0700deef07b32',
            'selectNum': '1',
            'klcn_value': 'R15CXFNNAw==',
            'ud_safe': 'QlxGVgEXClYJU0xaQVhRQAIFAVNGXhJZ',
            'Hm_lvt_52c42de35032567eb9d7a24a43c84bda': '1681301267,1681701370,1681876149,1681958442',
            'c__utma': '875156445.1068854496.281617177.1681890605.1681958442.64',
            'c__utmc': '875156445.1068854496',
            'Hm_lpvt_52c42de35032567eb9d7a24a43c84bda': '1681960985',
            'c__utmb': '875156445.1068854496.1681958442.1681960984.6',
            'userid_secure': 'Re187cCrc7GwZF3rkpNyepf0eJlZwiEXAjhrxwEXlGg1EuNxB07w07wqJXLcCewwGug0qMTIZ7R48OuSWN9NOLR+EnlpV7K2Q1ZlEfpFfRTVNchdUVgHsGbKtYc57nIboSnVP3H+HGwokfVi9cA2gC3hRzaRUL1l+e92qR9rBPL/upbqSCwschB2uyw9wPkYIZB+rymApX5rzG8JityBNiHJ/4ZaL+Ru+bC7jeb81CGYl8lW0vlG8Z2cGVZniUjPI0pufB6AuAMBMcdAbfxuBDXcrHL2YgYGpgmohpQN2PdD0shY5NYGwehyNZH8mO+/9mehx/AMIfKeD67IIZRHdSoqKjIwMjMtMDQtMTYgMDA6MDA6MDA=',
        }


        self.headers = {
            'authority': 'www.jianyu360.cn',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # Requests sorts cookies= alphabetically
            # 'cookie': 'SESSIONID=14584c6968b48f1519d251085ab0700deef07b32; SESSIONID=14584c6968b48f1519d251085ab0700deef07b32; selectNum=1; klcn_value=R15CXFNNAw==; ud_safe=QlxGVgEXClYJU0xaQVhRQAIFAVNGXhJZ; Hm_lvt_52c42de35032567eb9d7a24a43c84bda=1681301267,1681701370,1681876149,1681958442; c__utma=875156445.1068854496.281617177.1681890605.1681958442.64; c__utmc=875156445.1068854496; Hm_lpvt_52c42de35032567eb9d7a24a43c84bda=1681958508; c__utmb=875156445.1068854496.1681958442.1681958508.4; userid_secure=gRIvv65rNgLw/xSp7U0iyi61eczoVYZj3GNc8rSCC4AQ2biFfgbPUs+yTujv4zrMcPOlIULxvEoTBIovc0rA1wZT1pUe3SH3QLbI3VDNyFXG+jx6M0k93QmS0s5LI46ibgdNqaFwlpiP5fdSbaB0ETdVeaZKY/4yFaHLNvJofRxXFyXwlycY4RYFFttksfQhbtF+TFXLYR1NWYhvJsG8V0lp3zXvmh/wvvjySiROTokXwBJsRh4boYTr0Rcm/JyJ6tFyc+miDW770RvSLPdEV283+M+IEkGLku6uVExEqArFTHkWi85UzbTrTUunhw6fycA3IF6drvCzZHSTAuZ6gSoqKjIwMjMtMDQtMTYgMDA6MDA6MDA=',
            'origin': 'https://www.jianyu360.cn',
            'pragma': 'no-cache',
            'referer': 'https://www.jianyu360.cn/jylab/supsearch/index.html',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

    def search(self, keyword):

        print(f'search: {keyword}')
        data = {
            'pageNumber': '1',
            'pageSize': '150',
            'reqType': 'bidSearch',
            'searchvalue': keyword,
            'area': '',
            'subtype': '',
            'publishtime': '1681747200_1681747200',
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
            'searchGroup': '0',
            'searchMode': '0',
            'wordsMode': '0',
            'additionalWords': '',
        }

        response = requests.post('https://www.jianyu360.cn/front/pcAjaxReq',
                                 cookies=self.cookies,
                                 headers=self.headers,
                                 data=data)

        data = response.json()
        print(response.json())
        data_list = data.get('list')
        if not data_list:
            return

        for item in data_list:
            print(item['_id'])
            rds_206_11.sadd('jianyu:test:ids', item['_id'])

    def gen_key(self):
        key_list = rds_206_11.smembers('jianyu:9w_keyword_1')  # 这个keyword_1里面是过滤了一遍的
        rds_206_11.lpush('jianyu:test:keyword', *key_list)

    def main(self):

        while True:
            keyword = rds_206_11.lpop('jianyu:test:keyword')
            if not keyword:
                break
            self.search(keyword.decode())

            time.sleep(random.uniform(3,5))


if __name__ == '__main__':
    jy = Jianyu()
    # key = '大数据'
    # jy.search(key)
    jy.main()
    # jy.gen_key()
"""
17946个关键词

"""