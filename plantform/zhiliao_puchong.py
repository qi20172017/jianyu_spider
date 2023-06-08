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
import random
import time
from model.rds import rds_206_11
import requests
import re
from app.moen_app import moenApp
import json


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


def zhiliao(url):

    phone, userId, token = get_cookies()

    cookies = {
        'registered': 'true',
        'token': token,
        'role': '2',
        'userId': str(userId),
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://www.zhiliaobiaoxun.com/search/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    params = {
        'clickIndex': '1',
    }

    response = requests.get(url, params=params, cookies=cookies,verify=False,
                            headers=headers)
    print(response.text)

    rds_206_11.hincrby('zhiliao:cookies_count', phone)

    bid_type_tmp = re.findall('subtypeName:"(.*?)",', response.text)
    if bid_type_tmp:

        bid_type = bid_type_tmp[0]
        print(bid_type)
    else:
        bid_type = ''

    title_tmp = re.findall('title:"(.*?)",products', response.text)
    if title_tmp:
        # print(title[0])
        title = title_tmp[0]
        print(title)

    publish_time_tmp = re.findall('pubTime:"(.*?)",', response.text)
    if publish_time_tmp:
        publish_time = publish_time_tmp[0]
        print(publish_time)


    sourceUrl_tmp = re.findall('sourceUrl:"(.*?)",', response.text)
    if sourceUrl_tmp:
        # print(sourceUrl[0])
        a = sourceUrl_tmp[0]
        a.encode()
        a = '"'+a+'"'
        sourceUrl = eval(a)
        print(sourceUrl)
    else:
        sourceUrl = ''

    content_tmp = re.findall('content:"(.*?)",', response.text)
    if content_tmp:
        a = content_tmp[0]
        a.encode()
        a = '"'+a+'"'
        a = eval(a)
        # print(a)
        str_ = a.split('<head>')
        content = str_[0] + "<head>" + '<meta data-n-head="ssr" charset="utf-8">' + str_[1]
        print(content)
    else:
        content = ''

    bid_data = {

    }
    bid_data['publishtime'] = publish_time
    bid_data['title'] = title
    bid_data['subtype'] = bid_type
    bid_data['orign_link'] = sourceUrl
    bid_data['bid_detail'] = content
    bid_data['zl_url'] = url
    print(bid_data)
    if 'https://bid.snapshot.qudaobao.com.cn' in content:
        print('yes')

        file_url_list = re.findall('"https://bid\.snapshot\.qudaobao\.com\.cn/.*?"', content)

        try:
            file_url = file_url_list[0]
            print(file_url)

        except Exception as e:
            print(e)





        content = re.sub('"https://bid\.snapshot\.qudaobao\.com\.cn/.*?"', '""', content)
        bid_data['bid_detail'] = content

        print(bid_data['bid_detail'])

    moenApp.send_task('bid.zhiliao.clean', args=(json.dumps(bid_data),))



if __name__ == '__main__':

    """
    pdf链接不需要登录状态，就直接下下来，传到我们us3就行了。最好是把我们的us3地址，回填回去
    """

    url_list = [
        # 'https://www.zhiliaobiaoxun.com/content/491482417/b1',
        # 'https://www.zhiliaobiaoxun.com/content/398285379/b2'
        # 'https://www.zhiliaobiaoxun.com/content/398397378/b2'
        'https://www.zhiliaobiaoxun.com/content/398412253/b2'
    ]

    res = list(set(url_list))


    for url in res:
        zhiliao(url)
        time.sleep(random.uniform(10,30))


    # print(len(res))



    # eval('print("aa")')

    # a = "http:\u002F\u002Fwww.ebnew.com\u002FbusinessShow\u002F683232563.html"
    # print(a.encode().decode())
# a = "http:\u002F\u002Fwww.ebnew.com\u002FbusinessShow\u002F683232563.html"
    # print(a.encode().decode())

"""
https://www.zhiliaobiaoxun.com/content/307601484/b2
https://www.zhiliaobiaoxun.com/content/356258538/b2
https://www.zhiliaobiaoxun.com/content/373304101/b2
https://www.zhiliaobiaoxun.com/content/323437289/b2
https://www.zhiliaobiaoxun.com/content/323271993/b2
https://www.zhiliaobiaoxun.com/content/272931453/b2
https://www.zhiliaobiaoxun.com/content/316971442/b2
https://www.zhiliaobiaoxun.com/content/316971442/b2
https://www.zhiliaobiaoxun.com/content/317334898/b2
https://www.zhiliaobiaoxun.com/content/312658572/b2
https://www.zhiliaobiaoxun.com/content/296378007/b2
https://www.zhiliaobiaoxun.com/content/285829355/b2
https://www.zhiliaobiaoxun.com/content/285831309/b2
https://www.zhiliaobiaoxun.com/content/258019344/b2
https://www.zhiliaobiaoxun.com/content/273194226/b2
https://www.zhiliaobiaoxun.com/content/313862316/b2
https://www.zhiliaobiaoxun.com/content/275907038/b2
https://www.zhiliaobiaoxun.com/content/386998006/b2
https://www.zhiliaobiaoxun.com/content/316958160/b2
https://www.zhiliaobiaoxun.com/content/291410404/b2
https://www.zhiliaobiaoxun.com/content/276098010/b2
https://www.zhiliaobiaoxun.com/content/276098010/b2
https://www.zhiliaobiaoxun.com/content/276098010/b2
https://www.zhiliaobiaoxun.com/content/290047599/b2
https://www.zhiliaobiaoxun.com/content/321181197/b2
https://www.zhiliaobiaoxun.com/content/313180058/b2
https://www.zhiliaobiaoxun.com/content/313187620/b2
https://www.zhiliaobiaoxun.com/content/329453895/b2
https://www.zhiliaobiaoxun.com/content/306806768/b2
https://www.zhiliaobiaoxun.com/content/209671389/b2
https://www.zhiliaobiaoxun.com/content/307601484/b2
https://www.zhiliaobiaoxun.com/content/344854189/b2
https://www.zhiliaobiaoxun.com/content/386017644/b2
https://www.zhiliaobiaoxun.com/content/272931453/b2
https://www.zhiliaobiaoxun.com/content/313624475/b2
https://www.zhiliaobiaoxun.com/content/291410404/b2
https://www.zhiliaobiaoxun.com/content/321181197/b2
https://www.zhiliaobiaoxun.com/content/275907038/b2
https://www.zhiliaobiaoxun.com/content/369412907/b2
https://www.zhiliaobiaoxun.com/content/327615892/b2
https://www.zhiliaobiaoxun.com/content/273977588/b2
https://www.zhiliaobiaoxun.com/content/223339376/b2
https://www.zhiliaobiaoxun.com/content/319622052/b2
https://www.zhiliaobiaoxun.com/content/255663272/b2
https://www.zhiliaobiaoxun.com/content/171244344/b2
https://www.zhiliaobiaoxun.com/content/375954854/b2
https://www.zhiliaobiaoxun.com/content/373304101/b2
https://www.zhiliaobiaoxun.com/content/290047599/b2
https://www.zhiliaobiaoxun.com/content/339255256/b2
https://www.zhiliaobiaoxun.com/content/328124874/b2
https://www.zhiliaobiaoxun.com/content/312658572/b2
https://www.zhiliaobiaoxun.com/content/307572548/b2
https://www.zhiliaobiaoxun.com/content/282244181/b2
https://www.zhiliaobiaoxun.com/content/323437289/b2
https://www.zhiliaobiaoxun.com/content/307394925/b2
https://www.zhiliaobiaoxun.com/content/276098010/b2
https://www.zhiliaobiaoxun.com/content/227639034/b2
https://www.zhiliaobiaoxun.com/content/306825283/b2
https://www.zhiliaobiaoxun.com/content/206570162/b2
https://www.zhiliaobiaoxun.com/content/225420905/b2
https://www.zhiliaobiaoxun.com/content/224282450/b2
https://www.zhiliaobiaoxun.com/content/217456746/b2
https://www.zhiliaobiaoxun.com/content/324015441/b2
https://www.zhiliaobiaoxun.com/content/313187620/b2
https://www.zhiliaobiaoxun.com/content/296378007/b2
https://www.zhiliaobiaoxun.com/content/275574910/b2
https://www.zhiliaobiaoxun.com/content/273194226/b2
https://www.zhiliaobiaoxun.com/content/386998006/b2
https://www.zhiliaobiaoxun.com/content/313862316/b2
https://www.zhiliaobiaoxun.com/content/316958160/b2
https://www.zhiliaobiaoxun.com/content/285831309/b2
https://www.zhiliaobiaoxun.com/content/285829355/b2
https://www.zhiliaobiaoxun.com/content/329453895/b2
https://www.zhiliaobiaoxun.com/content/258019344/b2
"""

"""
16583189966
dckso847


17014204080
dsdk987.,



13810932928
gaochao!@#

"""