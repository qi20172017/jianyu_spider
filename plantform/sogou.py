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

    # url = "https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_="
    url = f"https://weixin.sogou.com/weixin?type=1&s_from=input&query={author}"

    payload = {}
    headers = {
        'authority': 'weixin.sogou.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        # 'cookie': 'SUID=F78BE28B24148B0A5F2961490003C686; wuid=AAEf9kFwMAAAAAqLFCSvhA0AXwU=; SUV=005935848BE28A455F6DA1927B0CD621; SMYUV=1602120640610882; ssuid=5042836920; pgv_pvi=3324632064; CXID=03AB5FFB1A948B7BEA4F2CD5F6F06E50; weixinIndexVisited=1; LSTMV=226%2C71; LCLKINT=2884; IPLOC=CN3100; UM_distinctid=17e0484f949641-09f9780291f303-36657407-13c680-17e0484f94ab93; ABTEST=2|1642989935|v1; JSESSIONID=aaaeVSxukh0-5-pnTFR5x; SNUID=461641368185570A3AA8E60C81D4D872; SUID=D541A4B43F18960A000000005F9C0667'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)

    x_data = etree.HTML(response.text)
    link = x_data.xpath('.//a[@uigs="account_article_0"]/@href')
    if link:
        link = link[0]
    else:
        return
    title = x_data.xpath('.//a[@uigs="account_article_0"]//text()')
    if title:
        title = ''.join(title)
    else:
        return
    create_time = x_data.xpath('//*[@id="sogou_vr_11002301_box_0"]/dl[2]/dd/span/text()')

    result_data = {}
    result_data['url'] = BASE_URL + link
    result_data['title'] = title
    result_data['author'] = author
    result_data['platform'] = 'sogou'
    result_data['article_id'] = hashlib.md5(title.encode()).hexdigest()
    result_data['item_id'] = hashlib.md5(title.encode()).hexdigest() + '@' + str(int(time.time()*1000))
    print(link)
    print(title)
    MyCsdnDao.upsert(**result_data)

if __name__ == '__main__':
    # page_data = get_data('weixin_43471909', 1)
    # page_data = get_data('kdl_csdn', 3)
    # clean_data(page_data)
    # print(int(time.time()*1000))
    get_data('菜鸟学Python编程')



    #https://weixin.sogou.com/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgS4MXq5w0X0EFN4shy8GTV-gH-cTfBJ3igVqXa8Fplpd9_hFo2Ahzt76-DPAQAQj8Gwoo2OAdiE4g2O-1ao_pgOdT89_qeCUbQlUIT23Tz3tC7nxI46TVGFXd1eNPhK_15jgIwlCg2zsmS8XDDMxAeiyP_CcLhYAPWXoJMxSrLpYvo6P_9As1grk7oyV86VK1KabhCRBjAVJyz9h9fEtpEx4tPujwwRB2Pw..&type=1&query=%E7%BD%91%E8%99%ABspider&token=F4C018F6461641368185570A3AA8E60C81D4D8726204AC96