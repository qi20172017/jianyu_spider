#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : sogou.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2022/2/10 下午2:10
@Desc  : 
"""
import hashlib
import time
from lxml import etree
import json
import requests

from app.moen_app import moenApp
from model.msql.my_dao.my_csdn_dao import MyCsdnDao

BASE_URL = "https://weixin.sogou.com"

@moenApp.task(
    name='moen.sogou.article',
    bind=True,
    acks_late=True,
    rate_limit='10/m',
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def get_data(self, author):

    BASE_URL = 'https://www.52pojie.cn/'
    # url = "https://www.52pojie.cn/forum.php?mod=forumdisplay&fid=5&typeid=378&filter=typeid&typeid=378&page=1&t=1792710"
    url = "https://www.52pojie.cn/forum.php?mod=forumdisplay&fid=5&typeid=378&filter=typeid&typeid=378&page=1"

    payload = {}
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.52pojie.cn/forum.php?mod=forumdisplay&fid=5&filter=typeid&typeid=378',
        'Accept-Language': 'en-US,en;q=0.9',
        # 'Cookie': 'htVC_2132_lastact=1648090895%09forum.php%09forumdisplay; htVC_2132_st_t=0%7C1648090895%7C627af139d59f0ea77f8b64ab8b616af3; htVC_2132_forum_lastvisit=D_5_1648090895; Hm_lvt_46d556462595ed05e05f009cdafff31a=1648091088; Hm_lpvt_46d556462595ed05e05f009cdafff31a=1648091088; __gads=ID=983242d495eb47fd-229c74c419d10047:T=1648091091:RT=1648091091:S=ALNI_MYJkh4MCuK7WjtaiKNcYmOH4zYNCQ; htVC_2132_atarget=1; htVC_2132_forum_lastvisit=D_5_1648091159; htVC_2132_lastact=1648091159%09forum.php%09forumdisplay; htVC_2132_lastvisit=1648087503; htVC_2132_saltkey=Rk6cQk0e; htVC_2132_st_t=0%7C1648091159%7C3cc0565cda5a42fca4f10566bf3c3362; htVC_2132_visitedfid=5'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

    # print(response.text)

    x_data = etree.HTML(response.text)
    table_data = x_data.xpath('.//table[@id="threadlisttableid"]/tbody')
    for item in table_data:
        title = xpath_data(item, './tr/th/a[2]/text()')
        link = xpath_data(item, './tr/th/a[2]/@href')

        author = xpath_data(item, './tr/td[2]/cite/a/@href')
        time_ = xpath_data(item,'./tr/td[2]/em/span/text()')
        view_count = xpath_data(item, './tr/td[3]/em/text()')
        comment_count = xpath_data(item, './tr/td[3]/a/text()')

        print(title, link, author, time_, comment_count, view_count)


        if title:
            result_data = {}
            result_data['url'] = BASE_URL + link
            result_data['title'] = title
            result_data['author'] = author
            result_data['platform'] = '52pj'
            result_data['article_id'] = hashlib.md5(title.encode()).hexdigest()
            result_data['item_id'] = hashlib.md5(title.encode()).hexdigest() + '@' + str(int(time.time()*1000))
            print(link)
            print(title)
            MyCsdnDao.upsert(**result_data)


def xpath_data(target, x):
    item = target.xpath(x)
    if item:
        return item[0]
    return ''



if __name__ == '__main__':
    # page_data = get_data('weixin_43471909', 1)
    # page_data = get_data('kdl_csdn', 3)
    # clean_data(page_data)
    # print(int(time.time()*1000))
    get_data('菜鸟学Python编程')



    #https://weixin.sogou.com/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgS4MXq5w0X0EFN4shy8GTV-gH-cTfBJ3igVqXa8Fplpd9_hFo2Ahzt76-DPAQAQj8Gwoo2OAdiE4g2O-1ao_pgOdT89_qeCUbQlUIT23Tz3tC7nxI46TVGFXd1eNPhK_15jgIwlCg2zsmS8XDDMxAeiyP_CcLhYAPWXoJMxSrLpYvo6P_9As1grk7oyV86VK1KabhCRBjAVJyz9h9fEtpEx4tPujwwRB2Pw..&type=1&query=%E7%BD%91%E8%99%ABspider&token=F4C018F6461641368185570A3AA8E60C81D4D8726204AC96

    "https://www.52pojie.cn/forum.php?mod=viewthread&tid=1521480&extra=page%3D1%26filter%3Dtypeid%26typeid%3D378"