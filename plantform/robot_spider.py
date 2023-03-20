#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : zl.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/2/10 下午3:35
@Desc  :
"""
import datetime
import platform
import requests
# from zlcx_login.zlcx_gold_login import user_pool
import redis
import hashlib
import time
import json
import math
RDS_HOST = '106.75.108.206'
RDS_PORT = 6380
RDS_PASSWORD = 'tianzhuanjiawa_009'


if 'Linux' == platform.system():
    print('Linux 平台')
    RDS_DB = 11
    source_topic = 'req_bid_to_spider'       # 正式
else:
    print(f'测试环境: {platform.system()}')
    RDS_DB = 14
    source_topic = 'req_bid_to_spider_test'  # 测试
    # RDS_DB = 11
    # source_topic = 'req_bid_to_spider'       # 正式

pool_206_11 = redis.ConnectionPool(host=RDS_HOST, port=RDS_PORT, db=RDS_DB, password=RDS_PASSWORD)
rds_206_11 = redis.StrictRedis(connection_pool=pool_206_11)


import json
import hashlib
import requests
from feapder.network.user_pool import GoldUser
from feapder.network.user_pool import GoldUserPool

headers = {
    'content-type': 'application/json;charset=utf-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}

max_page = 50

class CustomGoldUserPool(GoldUserPool):
    def login(self, user: GoldUser) -> GoldUser:
        # 此处为假数据，正常需通过登录网站获取cookie
        # time.sleep(60*5)
        username = user.username
        password = user.password
        pwd = hashlib.md5(password.encode('utf-8')).hexdigest()
        url = 'https://api-service-zhiliao.bailian-ai.com/login'
        data = {
            'password': pwd,
            'rememberMe': False,
            'smsCode': "",
            'username': username
        }
        res = requests.post(url=url, data=json.dumps(data), headers=headers, verify=False)
        data = res.json()
        if data['code'] == 1 and data['msg'] == 'OK':
            userId = data['data']['userId']
            token = data['data']['token']

            user.cookies = {'userId':userId,'token':token}
            return user

users = [
    GoldUser(
        username="13161748024",
        password="Datauseful",
        max_use_times=50000000,
        use_interval=(5, 10),
        login_interval=10
    )
]

user_pool = CustomGoldUserPool(
    "zlcx:user_pool",
    users=users,
    keep_alive=True,
)



def sign(data):
    str_md5 = hashlib.md5(data.encode(encoding='utf-8')).hexdigest()
    return str_md5

def self_login():
    username = "13161748024"
    password = "Datauseful"
    pwd = hashlib.md5(password.encode('utf-8')).hexdigest()
    url = 'https://api-service-zhiliao.bailian-ai.com/login'
    data = {
        'password': pwd,
        'rememberMe': False,
        'smsCode': "",
        'username': username
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers, verify=False)
    data = res.json()
    if data['code'] == 1 and data['msg'] == 'OK':
        userId = data['data']['userId']
        token = data['data']['token']

        # user.cookies = {'userId': userId, 'token': token}
        # return user
        print(token)
        return token

class Zl_spider():


    def __init__(self):


        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://www.zhiliaobiaoxun.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.zhiliaobiaoxun.com/company/5130/b1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            # 'auth-token': ,
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        self.auth = user_pool.get_user()
        self.headers["auth-token"] = self.auth.cookies['token']
        # self.headers["auth-token"] = 'eyJhbGciOiJIUzUxMiIsInppcCI6IkdaSVAifQ.H4sIAAAAAAAAAKtWykwsUbIyNDM3NzAzNTYx1VEqLk1SslIyMjI3s1TSUUqtKIBIG5oampuY1gIAtV7pnjEAAAA.6x7p21x6LT1K9tCI0V0e-gtfnjzvQcMRIfK5SNTumQIAbO7CzbKOWZ3dBFULXa-QIv5PC7CgabU7GBNjJghvgg'
        # self.userId = self.auth.cookies['userId']
        self.userId = 22769
        # self.userId = 21575

    def get_id(self, company_name):


        tmp_id = rds_206_11.hget('robot:company_id', company_name)
        if tmp_id:
            return tmp_id.decode()


        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://www.zhiliaobiaoxun.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.zhiliaobiaoxun.com/search?key=%E4%BC%98%E5%88%BB%E5%BE%97%E7%A7%91%E6%8A%80%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        params = {
            'page': '1',
            'count': '10',
            'keyword': company_name,
        }
        url = 'https://api-service-zhiliao.bailian-ai.com/search/org'
        response = requests.get(url, params=params, headers=headers)
        print(response.text)
        data = response.json().get('data')
        print(data)
        res_id = ''
        if data:
            records = data.get('records')
            for item in records:
                name = item.get('name')
                _id = item.get('id')
                if name == f"<font color='red'>{company_name}</font>":
                    res_id = _id
                rds_206_11.hset('robot:company_id', company_name, res_id)
        return res_id

    def search_bid(self, hash_lib_name, key, keyword, page):

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://www.zhiliaobiaoxun.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.zhiliaobiaoxun.com/search/?key=%E5%A4%A7%E6%95%B0%E6%8D%AE',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'auth-token': 'eyJhbGciOiJIUzUxMiIsInppcCI6IkdaSVAifQ.H4sIAAAAAAAAAKtWykwsUbIyNDO3MLA0MDIx1FEqLk1SslIyMjI3s1TSUUqtKIBIG5qbmZkY1gIAUewEHjEAAAA.Up-WtKOFm7g9qCs55EeQcq5A13NXpLRtX8GngA49k9vAs6G9MZM4AgLPyO8WbjBlM1ak8A7PL6jaD2Nqf_RC-g'

        }
        headers["auth-token"] = self_login()

        params = {
            'userId': self.userId,
            'page': page,
            'count': '50',
            'keyword': keyword,
        }

        # url = 'https://api-service-zhiliao.bailian-ai.com/search/bid'
        # data_dict = self.download(url, params)

        # 以前搜索没有登录，搜索的不多，换成登录后
        response = requests.get('https://api-service-zhiliao.bailian-ai.com/search/bid', params=params, headers=headers)
        data_dict = response.json()
        print('data_dict: ', data_dict)
        if not data_dict:
            print(f'search_bid: {params}')
            rds_206_11.hdel(hash_lib_name, key)
            return

        data = data_dict.get('data', {})
        total = data.get('total')
        if total:
            total = int(total)
        else:
            total = 1
        if data:
            data_list = data.get('records')
        else:
            data_list = []
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]

        if data_list:
            for item in data_list:
                print(item)
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'data': item}))
        else:
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'data': {}}))
        rds_206_11.hdel(hash_lib_name, key)
        return total


    def get_tag(self, hash_lib_name, key, orgId, type, page, bid_win_company=''):

        params = {
            'userId': self.userId,         # 账户id
            'orgIds': orgId,   # 公司的id
            'chooseStatus': '1',
            'type': type,                # 1 是招标   2是中标
            'sortType': '1',
            'isFollow': '0',
            'page': page,
            'count': '10',
            'id': orgId,   # 公司的id
            'bidMethods': '',
            'adcodes': '',
            'companyKeyword': bid_win_company,

        }


        print('get_tag: ', params)

        url = 'https://api-service-zhiliao.bailian-ai.com/company/bidding/detail'

        data_dict = self.download(url, params)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        data_list = data.get('records', [])
        total = int(data.get('total', 1))

        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]

        if data_list:
            for item in data_list:
                print(item)
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'data': item}))
        else:
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'data': {}}))
        rds_206_11.hdel(hash_lib_name, key)
        return total

    def entrance(self, hash_lib_name, key, orgId, page):

        params = {
            'userId': self.userId,
            'page': page,
            'sortType': '1',
            'count': '7',
            'orgId': orgId,
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/cac/entrance'
        data_dict = self.download(url, params)
        if not data_dict:
            return 1
        data = data_dict.get('data', {})
        total = data.get('total')
        if total:
            total = int(total)
        else:
            total = 1
        if data:
            data_list = data.get('records')
        else:
            data_list = []
        res = []
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        if data_list:
            for item in data_list:
                print(item)
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'data': item}))
        else:
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'data': {}}))
        rds_206_11.hdel(hash_lib_name, key)
        return total


    def E_parduct(self, hash_lib_name, key, orgId, page):

        params = {
            'userId': self.userId,
            'id': orgId,
            'type': '2',     # 中标type是2
            'keyword': '',
            'page': page,
            'count': '15',
            'chooseStatus': '1',
        }
        url = 'https://api-service-zhiliao.bailian-ai.com/company/bidding/product'
        data_dict = self.download(url, params)
        if not data_dict:
            return
        print(params, data_dict)
        data = data_dict.get('data', [])
        continue_ = data_dict.get('msg')
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        if not data:
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'product':{}}))
        else:
            for item in data:
                print(item)
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'product':item}))
        # rds_206_11.hdel(hash_lib_name, key)
        return continue_


    def F_parduct(self, hash_lib_name, key, orgId, page):
        params = {
            'userId': self.userId,
            'id': orgId,
            'type': '1',  # 招标是1
            'keyword': '',
            'page': page,
            'count': '15',
            'chooseStatus': '1',
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/company/bidding/product'
        data_dict = self.download(url, params)
        if not data_dict:
            return
        print(params, data_dict)
        data = data_dict.get('data', [])
        continue_ = data_dict.get('msg')
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        if not data:
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'product':{}}))
        else:
            for item in data:
                print(item)
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'product':item}))
        return continue_


    def getPartner(self, hash_lib_name, key, orgId, page, products_ids):
        """
        合作供应商
        """
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')

        params = {
            'userId': self.userId,
            'orgIds': orgId,
            'chooseStatus': '1',
            'type': '2',
            'isSubscribe': 'false',
            'startDate': '',
            'endDate': today_date,
            'productIds': products_ids,
            'adcode': '',
            'sortType': '1',
            'page': page,
            'count': '15',
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getPartner'
        data_dict = self.download(url, params)
        if not data_dict:
            return
        print(params, data_dict)
        data = data_dict.get('data')

        continue_ = data_dict.get('continue')

        if data:
            data_list = data.get('records')
        else:
            data_list = []
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        if not data_list:
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'data':{}}))
        else:
            for item in data_list:
                print(item)
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'data':item}))

        rds_206_11.hdel(hash_lib_name, key)

        return continue_

    def marketCount(self, hash_lib_name, keyword, start, end):
        """
        数据概览
        """

        json_data = {
            'startDate': start,
            'endDate': end,
            'keyword': keyword,
            'adcode': '',
            'matchType': 1,
            'excludeKeywords': '',
            'containKeywords': '',
            'userId': self.userId,
        }
        print(json_data)
        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/product/marketCount'
        data_dict = self.download(url, json=json_data)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        rds_206_11.sadd(res_hash_lib_name, json.dumps({'marketCount': data}))

        print('marketCount', data)

    def marketSize(self, hash_lib_name, keyword, start, end):
        """
        市场规模
        """

        json_data = {
            'startDate': start,
            'endDate': end,
            'keyword': keyword,
            'adcode': '',
            'matchType': 1,
            'excludeKeywords': '',
            'containKeywords': '',
            'dataType': 'month',
            'userId': self.userId,
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/product/marketSize'
        data_dict = self.download(url, json=json_data)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        rds_206_11.sadd(res_hash_lib_name, json.dumps({'marketSize': data}))

        print('marketSize', data)

    def marketSupply(self, hash_lib_name, keyword, start, end):
        """
        市场供需数量
        """

        json_data = {
            'startDate': start,
            'endDate': end,
            'keyword': keyword,
            'adcode': '',
            'matchType': 1,
            'excludeKeywords': '',
            'containKeywords': '',
            'dataType': 'year',
            'userId': self.userId,
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/product/marketSupply'
        data_dict = self.download(url, json=json_data)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        rds_206_11.sadd(res_hash_lib_name, json.dumps({'marketSupply': data}))

        print('marketSupply', data)


    def projectAmount(self, hash_lib_name, keyword, start, end):
        """
        项目金额区间分布
        """

        json_data = {
            'startDate': start,
            'endDate': end,
            'keyword': keyword,
            'adcode': '',
            'matchType': 1,
            'excludeKeywords': '',
            'containKeywords': '',
            'userId': self.userId,
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/product/projectAmount'
        data_dict = self.download(url, json=json_data)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        rds_206_11.sadd(res_hash_lib_name, json.dumps({'projectAmount': data}))
        print('projectAmount', data)


    def callerCountList(self, hash_lib_name, keyword, start, end):
        """
        各类采购商采购次数占比
        """

        json_data = {
            'startDate': start,
            'endDate': end,
            'keyword': keyword,
            'adcode': '',
            'matchType': 1,
            'excludeKeywords': '',
            'containKeywords': '',
            'userId': self.userId,
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/product/callerCountList'
        data_dict = self.download(url, json=json_data)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        rds_206_11.sadd(res_hash_lib_name, json.dumps({'callerCountList': data}))
        print('callerCountList', data)


    def callerMoneyList(self, hash_lib_name, keyword, start, end):
        """
        各类采购商采购金额占比
        """

        json_data = {
            'startDate': start,
            'endDate': end,
            'keyword': keyword,
            'adcode': '',
            'matchType': 1,
            'excludeKeywords': '',
            'containKeywords': '',
            'userId': self.userId,
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/product/callerMoneyList'
        data_dict = self.download(url, json=json_data)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        rds_206_11.sadd(res_hash_lib_name, json.dumps({'callerMoneyList': data}))
        print('callerMoneyList', data)


    def getOrgCountList(self, hash_lib_name, keyword, start, end):
        """
        采购 供应 代理机构排行
        """

        json_data = {
            'startDate': start,
            'endDate': end,
            'keyword': keyword,
            'adcode': '',
            'matchType': 1,
            'excludeKeywords': '',
            'containKeywords': '',
            'userId': self.userId,
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/product/getOrgCountList'
        data_dict = self.download(url, json=json_data)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        rds_206_11.sadd(res_hash_lib_name, json.dumps({'getOrgCountList': data}))
        print('getOrgCountList', data)


    def marketDistribution(self, hash_lib_name, keyword, start, end):
        """
        地区分布
        """

        json_data = {
            'startDate': start,
            'endDate': end,
            'keyword': keyword,
            'adcode': '',
            'matchType': 1,
            'excludeKeywords': '',
            'containKeywords': '',
            'sort': 2,                 # 按采购金额排序
            'regionType': 0,
            'userId': self.userId,
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/product/marketDistribution'
        data_dict = self.download(url, json=json_data)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
        rds_206_11.sadd(res_hash_lib_name, json.dumps({'marketDistribution': data}))
        print('marketDistribution', data)


    def F_getPartner(self, hash_lib_name, key, orgId, page, products_ids):

        today_date = datetime.datetime.today().strftime('%Y-%m-%d')

        params = {
            'userId': self.userId,
            'orgIds': orgId,
            'chooseStatus': '1',
            'type': '1',
            'isSubscribe': 'false',
            'startDate': '',
            'endDate': today_date,
            'productIds': products_ids,
            'sortType': '1',
            'page': page,
            'count': '15',
        }

        url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getPartner'

        data_dict = self.download(url, params)
        if not data_dict:
            return
        data = data_dict.get('data', {})
        data_list = data.get('records', [])
        total = data.get('continue', '')

        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]

        if data_list:
            for item in data_list:
                print(item)
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'F_getPartner': item}))
        else:
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'F_getPartner': {}}))
        rds_206_11.hdel(hash_lib_name, key)
        return total


    def download(self, url, params={}, json={}):

        if params != {} and json == {}:
            res = requests.get(url,
                                params=params,
                                # json=json,
                                headers=self.headers)
        elif params == {} and json != {}:
            res = requests.post(url,
                                json=json,
                                headers=self.headers)
        else:
            print(f'download error: params: {params}, json: {json}')
            return
        # url = 'https://api-service-zhiliao.bailian-ai.com/company/bidding/detail'
        # res = requests.get(url=url, params=params, headers=self.headers, proxies=proxies, verify=False)
        data = res.json()
        print(f'data:{data}')
        if '重新登' in data['msg']:
            user_pool.del_user(user_id=self.auth.user_id)
            self.auth = user_pool.get_user()
            self.headers["auth-token"] = self.auth.cookies['token']
            print(self.auth.cookies['token'])
            self.userId = self.auth.cookies['userId']
            return
        # if data['msg'] != "OK":
        #     print(data)
        #     raise Exception("请求异常。。")

        return data

    def company_search(self, hash_lib_name, key, task_info):
        print('company_search: ', task_info)
        params = task_info['params']

        keyword = params['keyword']
        page = params['page']


        total = self.search_bid(hash_lib_name, key, keyword, page)

        if int(page) == 1:
            for page in range(2, min(max_page, math.ceil(total/50))):
            # for page in range(2, 4):

                params['page'] = page
                task_info['params'] = params
                task_info['timestamp'] = time.time()
                j_data = json.dumps(task_info)
                request_id = sign(j_data)
                task_info['request_id'] = request_id
                j_data = json.dumps(task_info)
                rds_206_11.hset(hash_lib_name, request_id, j_data)

    def company_win_product(self, hash_lib_name, key, task_info):

        print('company_win_product: ', task_info)
        params = task_info['params']

        company_name = params['company_name']
        type = params['type']
        page = params['page']
        orgId = self.get_id(company_name)
        if not orgId:
            print('not orgid: ', task_info)
            self.error_case(hash_lib_name, task_info)
            rds_206_11.hdel(hash_lib_name, key)
            return
        total = self.get_tag(hash_lib_name, key, orgId, type, page)

        if int(page) == 1:
            for page in range(2, min(max_page, math.ceil(total/10))):
            # for page in range(2, 4):


                params['page'] = page

                task_info['params'] = params
                task_info['timestamp'] = time.time()

                j_data = json.dumps(task_info)
                request_id = sign(j_data)
                task_info['request_id'] = request_id
                j_data = json.dumps(task_info)

                rds_206_11.hset(hash_lib_name, request_id, j_data)

    def company_bidding_info(self, hash_lib_name, key, task_info):

        params = task_info['params']

        company_name = params['company_name']
        bid_win_company = params['bid_win_company']
        type = params['type']
        page = params['page']
        orgId = self.get_id(company_name)
        if not orgId:
            print('not orgid: ', task_info)
            self.error_case(hash_lib_name, task_info)
            rds_206_11.hdel(hash_lib_name, key)
            return
        total = self.get_tag(hash_lib_name, key, orgId, type, page, bid_win_company)
        if not total:
            total = 1
        if int(page) == 1:
            for page in range(2, min(max_page, math.ceil(total/10))):
            # for page in range(2, 4):
                params['page'] = page

                task_info['params'] = params
                task_info['timestamp'] = time.time()

                j_data = json.dumps(task_info)
                request_id = sign(j_data)
                task_info['request_id'] = request_id
                j_data = json.dumps(task_info)

                rds_206_11.hset(hash_lib_name, request_id, j_data)

    def company_competitor_analysis(self, hash_lib_name, key, task_info):

        params = task_info['params']

        company_name = params['company_name']
        page = params['page']
        orgId = self.get_id(company_name)
        if not orgId:
            print('not orgid: ', task_info)
            self.error_case(hash_lib_name, task_info)
            rds_206_11.hdel(hash_lib_name, key)
            return
        total = self.entrance(hash_lib_name, key, orgId, page)

        if int(page) == 1:
            for page in range(2, min(max_page, math.ceil(total/7))):
            # for page in range(2, 4):
                params['page'] = page
                task_info['params'] = params
                task_info['timestamp'] = time.time()

                j_data = json.dumps(task_info)
                request_id = sign(j_data)
                task_info['request_id'] = request_id
                j_data = json.dumps(task_info)

                rds_206_11.hset(hash_lib_name, request_id, j_data)

    # E  中标数据
    def company_cooperative_buyers(self, hash_lib_name, key, task_info):

        params = task_info['params']

        company_name = params['company_name']
        products_list = params['products_list']
        orgId = self.get_id(company_name)
        if not orgId:
            print('not orgid: ', task_info)
            self.error_case(hash_lib_name, task_info)
            rds_206_11.hdel(hash_lib_name, key)
            return
        products_ids = []
        if products_list:
            for product in products_list:
                p_id= self.search_product_id(2, orgId, product)
                if p_id == 0:
                    pass
                elif p_id == None:
                    return
                else:
                    products_ids.append(str(p_id))
            products_ids = ','.join(products_ids)
            if not products_ids:
                res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'getIndustry': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'getRegion': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'getOverview': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'getMoneyTrend': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'getCountTrend': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'data': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'product':{}}))
                rds_206_11.hdel(hash_lib_name, key)
                return

        product_page = params['product_page']
        partner_page = params['partner_page']

        today_date = datetime.datetime.today().strftime('%Y-%m-%d')

        if int(partner_page) == 1:
            params_q = {
                'userId': self.userId,
                'orgIds': orgId,
                'chooseStatus': '1',
                'type': '2',
                'isSubscribe': 'false',
                'startDate': '',
                'endDate': today_date,
                'productIds': products_ids,
                'adcode': '',
            }

            # 客户行业分布
            url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getIndustry'
            data_dict = self.download(url, params_q)
            if not data_dict:
                return
            data = data_dict.get('data', {})
            res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'getIndustry': data}))

            # 地区分布
            url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getRegion'
            data_dict = self.download(url, params_q)
            if not data_dict:
                return
            data = data_dict.get('data', {})
            res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'getRegion': data}))

            # 中标数据概览
            url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getOverview'
            data_dict = self.download(url, params_q)
            if not data_dict:
                return
            data = data_dict.get('data', {})
            res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'getOverview': data}))

            # 中标金额趋势
            url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getMoneyTrend'
            data_dict = self.download(url, params_q)
            if not data_dict:
                return
            data = data_dict.get('data', {})
            res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'getMoneyTrend': data}))

            # 中标次数趋势
            url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getCountTrend'
            data_dict = self.download(url, params_q)
            if not data_dict:
                return
            data = data_dict.get('data', {})
            res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'getCountTrend': data}))
        continue_ = None
        is_continue = None
        if partner_page != '-1':

            continue_ = self.getPartner(hash_lib_name, key, orgId, partner_page, products_ids)
        if product_page != '-1':
            is_continue = self.E_parduct(hash_lib_name, key, orgId, product_page)
        rds_206_11.hdel(hash_lib_name, key)

        if continue_ and int(partner_page) < max_page:
            page = int(partner_page)+1

            params['partner_page'] = page
            params['product_page'] = '-1'

            task_info['params'] = params
            task_info['timestamp'] = time.time()

            j_data = json.dumps(task_info)
            request_id = sign(j_data)
            task_info['request_id'] = request_id
            j_data = json.dumps(task_info)
            rds_206_11.hset(hash_lib_name, request_id, j_data)

        if is_continue == "OK" and int(product_page) < max_page:
            page = int(product_page)+1

            params['partner_page'] = '-1'
            params['product_page'] = page

            task_info['params'] = params
            task_info['timestamp'] = time.time()

            j_data = json.dumps(task_info)
            request_id = sign(j_data)
            task_info['request_id'] = request_id
            j_data = json.dumps(task_info)
            rds_206_11.hset(hash_lib_name, request_id, j_data)


    # F  招标数据
    def company_bidding_data(self, hash_lib_name, key, task_info):
        """
        企业分析页面，招标概览
        """

        print('company_bidding_data: ', task_info)

        params = task_info['params']

        company_name = params['company_name']
        products_list = params['products_list']
        orgId = self.get_id(company_name)

        if not orgId:
            print('not orgid: ', task_info)
            self.error_case(hash_lib_name, task_info)
            rds_206_11.hdel(hash_lib_name, key)
            return

        products_ids = []
        if products_list:
            for product in products_list:
                p_id= self.search_product_id(1, orgId, product)
                if p_id == 0:
                    pass
                elif p_id == None:
                    return
                else:
                    products_ids.append(str(p_id))
            products_ids = ','.join(products_ids)
            if not products_ids:
                res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'getMoneyTrend': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'getCountTrend': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'getOverview': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'F_getPartner': {}}))
                rds_206_11.sadd(res_hash_lib_name, json.dumps({'product': {}}))
                rds_206_11.hdel(hash_lib_name, key)
                return

        product_page = params['product_page']
        partner_page = params['partner_page']

        today_date = datetime.datetime.today().strftime('%Y-%m-%d')
        params_q = {
            'userId': self.userId,
            'orgIds': orgId,
            'chooseStatus': '1',
            'type': '1',
            'isSubscribe': 'false',
            'startDate': '',
            'endDate': today_date,
            'productIds': products_ids,
        }

        if int(partner_page) == 1:
            url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getMoneyTrend'
            data_dict = self.download(url, params_q)
            if not data_dict:
                return
            data = data_dict.get('data', {})
            res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'getMoneyTrend': data}))

            url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getCountTrend'
            data_dict = self.download(url, params_q)
            if not data_dict:
                return
            data = data_dict.get('data', {})
            res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'getCountTrend': data}))

            url = 'https://api-service-zhiliao.bailian-ai.com/analyse/company/getOverview'
            data_dict = self.download(url, params_q)
            if not data_dict:
                return
            data = data_dict.get('data', {})
            res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]
            rds_206_11.sadd(res_hash_lib_name, json.dumps({'getOverview': data}))

        is_true = None
        is_contue = None
        if partner_page != '-1':

            is_true = self.F_getPartner(hash_lib_name, key, orgId, partner_page, products_ids)

        if product_page != '-1':

            is_contue = self.F_parduct(hash_lib_name, key, orgId, product_page)

        rds_206_11.hdel(hash_lib_name, key)

        if is_true and int(partner_page) < max_page:

            page = int(partner_page)+1

            params['partner_page'] = page
            params['product_page'] = '-1'

            task_info['params'] = params
            task_info['timestamp'] = time.time()
            j_data = json.dumps(task_info)
            request_id = sign(j_data)
            task_info['request_id'] = request_id
            j_data = json.dumps(task_info)
            rds_206_11.hset(hash_lib_name, request_id, j_data)

        if is_contue and int(product_page) < max_page:
            page = int(product_page) + 1

            params['product_page'] = page
            params['partner_page'] = '-1'

            task_info['params'] = params
            task_info['timestamp'] = time.time()
            j_data = json.dumps(task_info)
            request_id = sign(j_data)
            task_info['request_id'] = request_id
            j_data = json.dumps(task_info)
            rds_206_11.hset(hash_lib_name, request_id, j_data)

    def company_product_data_report(self, hash_lib_name, key, task_info):
        params = task_info['params']

        keyword = params['product_name']

        today_date = datetime.datetime.today().strftime('%Y-%m-%d')
        today_list = today_date.split('-')
        end = today_date
        today_list[0] = '2018'
        start = '-'.join(today_list)
        self.marketCount(hash_lib_name, keyword, start, end)
        self.marketSize(hash_lib_name, keyword, start, end)
        self.marketSupply(hash_lib_name, keyword, start, end)
        self.projectAmount(hash_lib_name, keyword, start, end)
        self.callerCountList(hash_lib_name, keyword, start, end)
        self.callerMoneyList(hash_lib_name, keyword, start, end)
        self.getOrgCountList(hash_lib_name, keyword, start, end)
        self.marketDistribution(hash_lib_name, keyword, start, end)
        rds_206_11.hdel(hash_lib_name, key)

    def search_product_id(self, type, org_id, product):
        params = {
            'userId': '22769',
            'id': org_id,
            'type': type,
            'keyword': product,
            'page': '1',
            'chooseStatus': '1',
        }
        url = 'https://api-service-zhiliao.bailian-ai.com/company/bidding/product'

        data_dict = self.download(url, params)
        print('data:', data_dict)
        if not data_dict:
            return
        data = data_dict.get('data')
        for item in data:
            product_id = item.get('id', 0)
            product_name = item.get('name', '')
            if product_name == product:
                print(f'get id: {product_id}')
                return product_id
        return 0

    def error_case(self, hash_lib_name, data):
        res = {
            'error_msg': '没有id',
            'raw_data': data
        }
        res_hash_lib_name = 'robot:res:' + hash_lib_name[11:]

        rds_206_11.sadd(res_hash_lib_name, json.dumps({'error': res}))

    def main(self):

        while True:
            hash_libs = rds_206_11.keys('robot:task*')
            for hash_lib in hash_libs:

                hash_lib_name = hash_lib.decode()
                hkeys = rds_206_11.hkeys(hash_lib_name)
                if len(hkeys):
                    key = hkeys[-1].decode()
                else:
                    print('没有任务')
                    return

                task_info = json.loads(rds_206_11.hget(hash_lib_name, key).decode())
                spider_type = task_info['spider_type']
                params = task_info['params']
                print(params)

                if spider_type == "company_search":
                    self.company_search(hash_lib_name, key, task_info)       # A

                elif spider_type == "company_win_product":                          # B
                    self.company_win_product(hash_lib_name, key, task_info)

                elif spider_type == "company_bidding_info":                   # D
                    self.company_bidding_info(hash_lib_name, key, task_info)

                elif spider_type == "company_competitor_analysis":
                    self.company_competitor_analysis(hash_lib_name, key, task_info)  # C

                elif spider_type == "company_cooperative_buyers":
                    self.company_cooperative_buyers(hash_lib_name, key, task_info)  # E

                elif spider_type == "company_bidding_data":
                    self.company_bidding_data(hash_lib_name, key, task_info)  # F

                elif spider_type == "company_product_data_report":
                    print(f'{spider_type}: {task_info}')
                    self.company_product_data_report(hash_lib_name, key, task_info)   # G


                time.sleep(1)
            time.sleep(3)



if __name__ == '__main__':
    userId= '22769'
    orgId= '981377'
    type= '1'

    page= '2'

    # self_login()

    # get_tag(userId, orgId, type, page)
    # contender(userId, orgId, page)
    # getMoneyTrend()
    # getCountTrend()
    # getOverview()
    # getPartner()
    # marketCount()
    # marketSize()
    # marketSupply()
    # projectAmount()
    # callerCountList()
    # callerMoneyList()
    # getOrgCountList()
    zl_spider = Zl_spider()
    zl_spider.main()
    # zl_spider.search_bid('1','2', '广州亮风台信息科技有限公司', '1')
    # zl_spider.search_product_id('1','405341986', '五金')


    # zl_spider.search_bid()

    # zl_spider.bid_info('11','22', '197', '2')
    # _id = zl_spider.get_id('优刻得科技股份有限公司')
    #
    # print(_id)