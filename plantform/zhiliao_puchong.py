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
# from .jianyu import upload_us3
from common.us import UfileOss
import os
from plantform.zhiliao import sign

test = True

if test:
    folder_name = "other_test/"
else:
    folder_name = "other_bid"


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
    response = requests.get(pdf_url,
                            headers=headers)

    return response.content



def zhiliao(url):

    phone, userId, token = get_cookies()

    # phone = '13161748024'
    # userId = '22769'
    # token = 'eyJhbGciOiJIUzUxMiIsInppcCI6IkdaSVAifQ.H4sIAAAAAAAAAKtWykwsUbIyNLMwMzMxNTI111EqLk1SslIyMjI3s1TSUUqtKIBImxsbmpma1wIApR5EujEAAAA.pUjtu9yiCbU3YkfWHSvjd2LGhtQIOMU2LkdysLmGPc0jIT7tIhLExLkVfy0tUSNVKDJ03JYrw98UtppEnRfQjw'

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
    bid_data['detail_type'] = 'html'

    bid_data['uuid'] = sign(url)

    print(bid_data)
    # if 'https://bid.snapshot.qudaobao.com.cn' in content:
    #     file_url_list = re.findall('"(https://bid\.snapshot\.qudaobao\.com\.cn/.*?)"', content)
    #     try:
    #         file_url = file_url_list[0]
    #         print(file_url)
    #         bid_data['bid_detail'] = downlond(file_url)
    #         if '.pdf' in file_url:
    #             bid_data['detail_type'] = 'pdf'
    #     except Exception as e:
    #         print(e)
    #         content = re.sub('"https://bid\.snapshot\.qudaobao\.com\.cn/.*?"', '""', content)
    #         bid_data['bid_detail'] = content
    #     print(bid_data['bid_detail'])
    #
    # # "https://bid.snapshot.qudaobao.com.cn/46d002b9cfcfc59b3dbf2946a54b0973c340585d.pdf"

    bid_data['filepath'] = upload_us3(bid_data)
    del bid_data['detail_type']
    print(bid_data)
    moenApp.send_task('bid.zhiliao.clean', args=(json.dumps(bid_data),))


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




if __name__ == '__main__':

    """
    pdf链接不需要登录状态，就直接下下来，传到我们us3就行了。最好是把我们的us3地址，回填回去
    """


    url_list = ['https://www.zhiliaobiaoxun.com/content/516773969/b1',
                'https://www.zhiliaobiaoxun.com/content/516815831/b1',
                'https://www.zhiliaobiaoxun.com/content/418826706/b2',
                'https://www.zhiliaobiaoxun.com/content/516811685/b1',
                'https://www.zhiliaobiaoxun.com/content/418834308/b2',
                'https://www.zhiliaobiaoxun.com/content/418843253/b2',
                'https://www.zhiliaobiaoxun.com/content/516784270/b1',
                'https://www.zhiliaobiaoxun.com/content/516834656/b1',
                'https://www.zhiliaobiaoxun.com/content/516773361/b1',
                'https://www.zhiliaobiaoxun.com/content/516832393/b1',
                'https://www.zhiliaobiaoxun.com/content/516835383/b1',
                'https://www.zhiliaobiaoxun.com/content/516833369/b1',
                'https://www.zhiliaobiaoxun.com/content/418872724/b2',
                'https://www.zhiliaobiaoxun.com/content/418869478/b2',
                'https://www.zhiliaobiaoxun.com/content/418886106/b2',
                'https://www.zhiliaobiaoxun.com/content/516831731/b1',
                'https://www.zhiliaobiaoxun.com/content/418883419/b2',
                'https://www.zhiliaobiaoxun.com/content/516832269/b1',
                'https://www.zhiliaobiaoxun.com/content/418880855/b2',
                'https://www.zhiliaobiaoxun.com/content/516834363/b1',
                'https://www.zhiliaobiaoxun.com/content/418884616/b2',
                'https://www.zhiliaobiaoxun.com/content/418882808/b2',
                'https://www.zhiliaobiaoxun.com/content/516831623/b1',
                'https://www.zhiliaobiaoxun.com/content/418887045/b2',
                'https://www.zhiliaobiaoxun.com/content/418885143/b2',
                'https://www.zhiliaobiaoxun.com/content/516834519/b1',
                'https://www.zhiliaobiaoxun.com/content/418887058/b2',
                'https://www.zhiliaobiaoxun.com/content/418880165/b2',
                'https://www.zhiliaobiaoxun.com/content/418883141/b2',
                'https://www.zhiliaobiaoxun.com/content/418886593/b2',
                'https://www.zhiliaobiaoxun.com/content/418883260/b2',
                'https://www.zhiliaobiaoxun.com/content/418881959/b2',
                'https://www.zhiliaobiaoxun.com/content/516779294/b1',
                'https://www.zhiliaobiaoxun.com/content/418768198/b2',
                'https://www.zhiliaobiaoxun.com/content/516772611/b1',
                'https://www.zhiliaobiaoxun.com/content/418826898/b2',
                'https://www.zhiliaobiaoxun.com/content/516772003/b1',
                'https://www.zhiliaobiaoxun.com/content/516818345/b1',
                'https://www.zhiliaobiaoxun.com/content/516770309/b1',
                'https://www.zhiliaobiaoxun.com/content/516785255/b1',
                'https://www.zhiliaobiaoxun.com/content/418841609/b2',
                'https://www.zhiliaobiaoxun.com/content/516773488/b1',
                'https://www.zhiliaobiaoxun.com/content/516784384/b1',
                'https://www.zhiliaobiaoxun.com/content/418822334/b2',
                'https://www.zhiliaobiaoxun.com/content/418832137/b2',
                'https://www.zhiliaobiaoxun.com/content/516786445/b1',
                'https://www.zhiliaobiaoxun.com/content/418825507/b2',
                'https://www.zhiliaobiaoxun.com/content/418827193/b2',
                'https://www.zhiliaobiaoxun.com/content/516818918/b1',
                'https://www.zhiliaobiaoxun.com/content/418837315/b2',
                'https://www.zhiliaobiaoxun.com/content/516788306/b1',
                'https://www.zhiliaobiaoxun.com/content/418862236/b2',
                'https://www.zhiliaobiaoxun.com/content/418810847/b2',
                'https://www.zhiliaobiaoxun.com/content/516815872/b1',
                'https://www.zhiliaobiaoxun.com/content/418794768/b2',
                'https://www.zhiliaobiaoxun.com/content/418791922/b2',
                'https://www.zhiliaobiaoxun.com/content/516775624/b1',
                'https://www.zhiliaobiaoxun.com/content/418835393/b2',
                'https://www.zhiliaobiaoxun.com/content/418852034/b2',
                'https://www.zhiliaobiaoxun.com/content/418809677/b2',
                'https://www.zhiliaobiaoxun.com/content/516811685/b1',
                'https://www.zhiliaobiaoxun.com/content/418861484/b2',
                'https://www.zhiliaobiaoxun.com/content/418822607/b2',
                'https://www.zhiliaobiaoxun.com/content/418822585/b2',
                'https://www.zhiliaobiaoxun.com/content/418838859/b2',
                'https://www.zhiliaobiaoxun.com/content/516821325/b1',
                'https://www.zhiliaobiaoxun.com/content/418751880/b2',
                'https://www.zhiliaobiaoxun.com/content/418764730/b2',
                'https://www.zhiliaobiaoxun.com/content/418798906/b2',
                'https://www.zhiliaobiaoxun.com/content/418860027/b2',
                'https://www.zhiliaobiaoxun.com/content/418785665/b2',
                'https://www.zhiliaobiaoxun.com/content/418772835/b2',
                'https://www.zhiliaobiaoxun.com/content/418790639/b2',
                'https://www.zhiliaobiaoxun.com/content/418760323/b2',
                'https://www.zhiliaobiaoxun.com/content/516777775/b1',
                'https://www.zhiliaobiaoxun.com/content/516815099/b1',
                'https://www.zhiliaobiaoxun.com/content/516781269/b1',
                'https://www.zhiliaobiaoxun.com/content/418827918/b2',
                'https://www.zhiliaobiaoxun.com/content/516804582/b1',
                'https://www.zhiliaobiaoxun.com/content/418876078/b2',
                'https://www.zhiliaobiaoxun.com/content/418813598/b2',
                'https://www.zhiliaobiaoxun.com/content/418770767/b2',
                'https://www.zhiliaobiaoxun.com/content/418840775/b2',
                'https://www.zhiliaobiaoxun.com/content/418822581/b2',
                'https://www.zhiliaobiaoxun.com/content/516821197/b1',
                'https://www.zhiliaobiaoxun.com/content/418822595/b2',
                'https://www.zhiliaobiaoxun.com/content/418854479/b2',
                'https://www.zhiliaobiaoxun.com/content/516809128/b1',
                'https://www.zhiliaobiaoxun.com/content/516780658/b1',
                'https://www.zhiliaobiaoxun.com/content/418815925/b2',
                'https://www.zhiliaobiaoxun.com/content/418834718/b2',
                'https://www.zhiliaobiaoxun.com/content/418863102/b2',
                'https://www.zhiliaobiaoxun.com/content/418793549/b2',
                'https://www.zhiliaobiaoxun.com/content/516804889/b1',
                'https://www.zhiliaobiaoxun.com/content/418796754/b2',
                'https://www.zhiliaobiaoxun.com/content/516796919/b1',
                'https://www.zhiliaobiaoxun.com/content/418822609/b2',
                'https://www.zhiliaobiaoxun.com/content/418852559/b2',
                'https://www.zhiliaobiaoxun.com/content/418838239/b2',
                'https://www.zhiliaobiaoxun.com/content/418846149/b2',
                'https://www.zhiliaobiaoxun.com/content/418820669/b2',
                'https://www.zhiliaobiaoxun.com/content/418815575/b2',
                'https://www.zhiliaobiaoxun.com/content/516790656/b1',
                'https://www.zhiliaobiaoxun.com/content/418839020/b2',
                'https://www.zhiliaobiaoxun.com/content/418759053/b2',
                'https://www.zhiliaobiaoxun.com/content/418827171/b2',
                'https://www.zhiliaobiaoxun.com/content/418865932/b2',
                'https://www.zhiliaobiaoxun.com/content/418877623/b2',
                'https://www.zhiliaobiaoxun.com/content/516802770/b1',
                'https://www.zhiliaobiaoxun.com/content/418817044/b2',
                'https://www.zhiliaobiaoxun.com/content/418834706/b2',
                'https://www.zhiliaobiaoxun.com/content/418832020/b2',
                'https://www.zhiliaobiaoxun.com/content/516830700/b1',
                'https://www.zhiliaobiaoxun.com/content/516789532/b1',
                'https://www.zhiliaobiaoxun.com/content/418838621/b2',
                'https://www.zhiliaobiaoxun.com/content/516817204/b1',
                'https://www.zhiliaobiaoxun.com/content/418769299/b2',
                'https://www.zhiliaobiaoxun.com/content/418850782/b2',
                'https://www.zhiliaobiaoxun.com/content/516773981/b1',
                'https://www.zhiliaobiaoxun.com/content/516777063/b1',
                'https://www.zhiliaobiaoxun.com/content/516807654/b1',
                'https://www.zhiliaobiaoxun.com/content/516788077/b1',
                'https://www.zhiliaobiaoxun.com/content/418759009/b2',
                'https://www.zhiliaobiaoxun.com/content/516820436/b1',
                'https://www.zhiliaobiaoxun.com/content/418837466/b2',
                'https://www.zhiliaobiaoxun.com/content/418814734/b2',
                'https://www.zhiliaobiaoxun.com/content/516787276/b1',
                'https://www.zhiliaobiaoxun.com/content/516776895/b1',
                'https://www.zhiliaobiaoxun.com/content/418857453/b2',
                'https://www.zhiliaobiaoxun.com/content/418863593/b2',
                'https://www.zhiliaobiaoxun.com/content/418830884/b2',
                'https://www.zhiliaobiaoxun.com/content/516760470/b1',
                'https://www.zhiliaobiaoxun.com/content/516794450/b1',
                'https://www.zhiliaobiaoxun.com/content/516804932/b1',
                'https://www.zhiliaobiaoxun.com/content/418858353/b2',
                'https://www.zhiliaobiaoxun.com/content/418843693/b2',
                'https://www.zhiliaobiaoxun.com/content/418880745/b2',
                'https://www.zhiliaobiaoxun.com/content/516773652/b1',
                'https://www.zhiliaobiaoxun.com/content/418863338/b2',
                'https://www.zhiliaobiaoxun.com/content/418875323/b2',
                'https://www.zhiliaobiaoxun.com/content/516830425/b1',
                'https://www.zhiliaobiaoxun.com/content/516792940/b1',
                'https://www.zhiliaobiaoxun.com/content/516772535/b1',
                'https://www.zhiliaobiaoxun.com/content/418869155/b2',
                'https://www.zhiliaobiaoxun.com/content/418864765/b2',
                'https://www.zhiliaobiaoxun.com/content/516821791/b1',
                'https://www.zhiliaobiaoxun.com/content/418833427/b2',
                'https://www.zhiliaobiaoxun.com/content/418870787/b2',
                'https://www.zhiliaobiaoxun.com/content/418874813/b2',
                'https://www.zhiliaobiaoxun.com/content/418861958/b2',
                'https://www.zhiliaobiaoxun.com/content/516812588/b1',
                'https://www.zhiliaobiaoxun.com/content/418872716/b2',
                'https://www.zhiliaobiaoxun.com/content/516779890/b1',
                'https://www.zhiliaobiaoxun.com/content/516802179/b1',
                'https://www.zhiliaobiaoxun.com/content/418855170/b2',
                'https://www.zhiliaobiaoxun.com/content/418875276/b2',
                'https://www.zhiliaobiaoxun.com/content/516803507/b1',
                'https://www.zhiliaobiaoxun.com/content/418769313/b2',
                'https://www.zhiliaobiaoxun.com/content/516794287/b1',
                'https://www.zhiliaobiaoxun.com/content/516784946/b1',
                'https://www.zhiliaobiaoxun.com/content/516761739/b1',
                'https://www.zhiliaobiaoxun.com/content/418843253/b2',
                'https://www.zhiliaobiaoxun.com/content/516773969/b1',
                'https://www.zhiliaobiaoxun.com/content/418846879/b2',
                'https://www.zhiliaobiaoxun.com/content/516774097/b1',
                'https://www.zhiliaobiaoxun.com/content/418869186/b2',
                'https://www.zhiliaobiaoxun.com/content/418767204/b2',
                'https://www.zhiliaobiaoxun.com/content/418825512/b2',
                'https://www.zhiliaobiaoxun.com/content/418759044/b2',
                'https://www.zhiliaobiaoxun.com/content/418843230/b2',
                'https://www.zhiliaobiaoxun.com/content/418783077/b2',
                'https://www.zhiliaobiaoxun.com/content/418837031/b2',
                'https://www.zhiliaobiaoxun.com/content/418796061/b2',
                'https://www.zhiliaobiaoxun.com/content/418852633/b2',
                'https://www.zhiliaobiaoxun.com/content/516813772/b1',
                'https://www.zhiliaobiaoxun.com/content/418744501/b2',
                'https://www.zhiliaobiaoxun.com/content/418824781/b2',
                'https://www.zhiliaobiaoxun.com/content/516809636/b1',
                'https://www.zhiliaobiaoxun.com/content/418841189/b2',
                'https://www.zhiliaobiaoxun.com/content/516766394/b1',
                'https://www.zhiliaobiaoxun.com/content/516788361/b1',
                'https://www.zhiliaobiaoxun.com/content/516766461/b1',
                'https://www.zhiliaobiaoxun.com/content/516779889/b1',
                'https://www.zhiliaobiaoxun.com/content/516813363/b1',
                'https://www.zhiliaobiaoxun.com/content/418819511/b2',
                'https://www.zhiliaobiaoxun.com/content/516797742/b1',
                'https://www.zhiliaobiaoxun.com/content/516776088/b1',
                'https://www.zhiliaobiaoxun.com/content/516751883/b1',
                'https://www.zhiliaobiaoxun.com/content/516811529/b1',
                'https://www.zhiliaobiaoxun.com/content/418839177/b2',
                'https://www.zhiliaobiaoxun.com/content/516784270/b1',
                'https://www.zhiliaobiaoxun.com/content/516786183/b1',
                'https://www.zhiliaobiaoxun.com/content/516817927/b1',
                'https://www.zhiliaobiaoxun.com/content/516799875/b1',
                'https://www.zhiliaobiaoxun.com/content/516788447/b1',
                'https://www.zhiliaobiaoxun.com/content/516770403/b1',
                'https://www.zhiliaobiaoxun.com/content/516819751/b1',
                'https://www.zhiliaobiaoxun.com/content/516780692/b1',
                'https://www.zhiliaobiaoxun.com/content/418820381/b2',
                'https://www.zhiliaobiaoxun.com/content/418859602/b2',
                'https://www.zhiliaobiaoxun.com/content/516785249/b1',
                'https://www.zhiliaobiaoxun.com/content/516807967/b1',
                'https://www.zhiliaobiaoxun.com/content/516808731/b1',
                'https://www.zhiliaobiaoxun.com/content/516831565/b1',
                'https://www.zhiliaobiaoxun.com/content/418857841/b2',
                'https://www.zhiliaobiaoxun.com/content/418823754/b2',
                'https://www.zhiliaobiaoxun.com/content/418869822/b2',
                'https://www.zhiliaobiaoxun.com/content/418848085/b2',
                'https://www.zhiliaobiaoxun.com/content/516806626/b1',
                'https://www.zhiliaobiaoxun.com/content/516794287/b1',
                'https://www.zhiliaobiaoxun.com/content/418859189/b2',
                'https://www.zhiliaobiaoxun.com/content/516794041/b1',
                'https://www.zhiliaobiaoxun.com/content/516816796/b1',
                'https://www.zhiliaobiaoxun.com/content/418830973/b2',
                'https://www.zhiliaobiaoxun.com/content/516795554/b1',
                'https://www.zhiliaobiaoxun.com/content/516773643/b1',
                'https://www.zhiliaobiaoxun.com/content/418825254/b2',
                'https://www.zhiliaobiaoxun.com/content/516762318/b1',

                ]


    res = list(set(url_list))
    # print(res)

    # print(len(res))
    # zhiliao('https://www.zhiliaobiaoxun.com/content/398397378/b2')

    for url in res:
        try:
            print('current: ', url)
            zhiliao(url)
        except Exception as e:
            print(e)
        time.sleep(random.uniform(10, 30))
        # print(url)

    # print(len(res))



