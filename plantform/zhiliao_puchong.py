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
        print(bid_data['bid_detail'])

    # "https://bid.snapshot.qudaobao.com.cn/46d002b9cfcfc59b3dbf2946a54b0973c340585d.pdf"

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


    url_list = [
        "https://www.zhiliaobiaoxun.com/content/402274067/b2",
        "https://www.zhiliaobiaoxun.com/content/402670198/b2",
        "https://www.zhiliaobiaoxun.com/content/401711682/b2",
        "https://www.zhiliaobiaoxun.com/content/395535824/b2",
        "https://www.zhiliaobiaoxun.com/content/394141376/b2",
        "https://www.zhiliaobiaoxun.com/content/394057405/b2",
        "https://www.zhiliaobiaoxun.com/content/390291982/b2",
        "https://www.zhiliaobiaoxun.com/content/387341677/b2",
        "https://www.zhiliaobiaoxun.com/content/382015091/b2",
        "https://www.zhiliaobiaoxun.com/content/366327571/b2",
        "https://www.zhiliaobiaoxun.com/content/363977976/b2",
        "https://www.zhiliaobiaoxun.com/content/364018422/b2",
        "https://www.zhiliaobiaoxun.com/content/359003228/b2",
        "https://www.zhiliaobiaoxun.com/content/354412804/b2",
        "https://www.zhiliaobiaoxun.com/content/352806913/b2",
        "https://www.zhiliaobiaoxun.com/content/350324059/b2",
        "https://www.zhiliaobiaoxun.com/content/349252522/b2",
        "https://www.zhiliaobiaoxun.com/content/347005549/b2",
        "https://www.zhiliaobiaoxun.com/content/346146532/b2",
        "https://www.zhiliaobiaoxun.com/content/346216705/b2",
        "https://www.zhiliaobiaoxun.com/content/343282249/b2",
        "https://www.zhiliaobiaoxun.com/content/341572720/b2",
        "https://www.zhiliaobiaoxun.com/content/341050613/b2",
        "https://www.zhiliaobiaoxun.com/content/380989027/b2",
        "https://www.zhiliaobiaoxun.com/content/335295151/b2",
        "https://www.zhiliaobiaoxun.com/content/334007357/b2",
        "https://www.zhiliaobiaoxun.com/content/380990277/b2",
        "https://www.zhiliaobiaoxun.com/content/333381509/b2",
        "https://www.zhiliaobiaoxun.com/content/330710795/b2",
        "https://www.zhiliaobiaoxun.com/content/381009082/b2",
        "https://www.zhiliaobiaoxun.com/content/327226207/b2",
        "https://www.zhiliaobiaoxun.com/content/327232943/b2",
        "https://www.zhiliaobiaoxun.com/content/327080516/b2",
        "https://www.zhiliaobiaoxun.com/content/381014201/b2",
        "https://www.zhiliaobiaoxun.com/content/326451426/b2",
        "https://www.zhiliaobiaoxun.com/content/327246061/b2",
        "https://www.zhiliaobiaoxun.com/content/325801440/b2",
        "https://www.zhiliaobiaoxun.com/content/381024359/b2",
        "https://www.zhiliaobiaoxun.com/content/381032174/b2",
        "https://www.zhiliaobiaoxun.com/content/321587811/b2",
        "https://www.zhiliaobiaoxun.com/content/317175285/b2",
        "https://www.zhiliaobiaoxun.com/content/381035565/b2",
        "https://www.zhiliaobiaoxun.com/content/381079929/b2",
        "https://www.zhiliaobiaoxun.com/content/297909451/b2",
        "https://www.zhiliaobiaoxun.com/content/295117649/b2",
        "https://www.zhiliaobiaoxun.com/content/306218115/b2",
        "https://www.zhiliaobiaoxun.com/content/293192785/b2",
        "https://www.zhiliaobiaoxun.com/content/381184954/b2",
        "https://www.zhiliaobiaoxun.com/content/320699559/b2",
        "https://www.zhiliaobiaoxun.com/content/320374298/b2",
        "https://www.zhiliaobiaoxun.com/content/381236046/b2",
        "https://www.zhiliaobiaoxun.com/content/381267559/b2",
        "https://www.zhiliaobiaoxun.com/content/385910954/b2",
        "https://www.zhiliaobiaoxun.com/content/321642571/b2",
        "https://www.zhiliaobiaoxun.com/content/285413912/b2",
        "https://www.zhiliaobiaoxun.com/content/283208602/b2",
        "https://www.zhiliaobiaoxun.com/content/302358093/b2",
        "https://www.zhiliaobiaoxun.com/content/282980886/b2",
        "https://www.zhiliaobiaoxun.com/content/282882960/b2",
        "https://www.zhiliaobiaoxun.com/content/374375898/b2",
        "https://www.zhiliaobiaoxun.com/content/282901662/b2",
        "https://www.zhiliaobiaoxun.com/content/282729429/b2",
        "https://www.zhiliaobiaoxun.com/content/284410882/b2",
        "https://www.zhiliaobiaoxun.com/content/321647164/b2",
        "https://www.zhiliaobiaoxun.com/content/289583614/b2",
        "https://www.zhiliaobiaoxun.com/content/263452832/b2",
        "https://www.zhiliaobiaoxun.com/content/336446760/b2",
        "https://www.zhiliaobiaoxun.com/content/318480680/b2",
        "https://www.zhiliaobiaoxun.com/content/334882339/b2",
        "https://www.zhiliaobiaoxun.com/content/393137487/b2",
        "https://www.zhiliaobiaoxun.com/content/243429148/b2",
        "https://www.zhiliaobiaoxun.com/content/402669150/b2",
        "https://www.zhiliaobiaoxun.com/content/304658882/b2",
        "https://www.zhiliaobiaoxun.com/content/319815174/b2",
        "https://www.zhiliaobiaoxun.com/content/295372838/b2",
        "https://www.zhiliaobiaoxun.com/content/334886991/b2",
        "https://www.zhiliaobiaoxun.com/content/304707225/b2",
        "https://www.zhiliaobiaoxun.com/content/381567900/b2",
        "https://www.zhiliaobiaoxun.com/content/381576464/b2",
        "https://www.zhiliaobiaoxun.com/content/324956715/b2",
        "https://www.zhiliaobiaoxun.com/content/287997970/b2",
        "https://www.zhiliaobiaoxun.com/content/219910865/b2",
        "https://www.zhiliaobiaoxun.com/content/282980878/b2",
        "https://www.zhiliaobiaoxun.com/content/310843475/b2",
        "https://www.zhiliaobiaoxun.com/content/353796554/b2",
        "https://www.zhiliaobiaoxun.com/content/282357255/b2",
        "https://www.zhiliaobiaoxun.com/content/283006359/b2",
        "https://www.zhiliaobiaoxun.com/content/263466880/b2",
        "https://www.zhiliaobiaoxun.com/content/206061168/b2",
        "https://www.zhiliaobiaoxun.com/content/206060744/b2",
        "https://www.zhiliaobiaoxun.com/content/221729788/b2",
        "https://www.zhiliaobiaoxun.com/content/282359001/b2",
        "https://www.zhiliaobiaoxun.com/content/206009479/b2",
        "https://www.zhiliaobiaoxun.com/content/205621545/b2",
        "https://www.zhiliaobiaoxun.com/content/282358658/b2",
        "https://www.zhiliaobiaoxun.com/content/336417569/b2",
        "https://www.zhiliaobiaoxun.com/content/295556219/b2",
        "https://www.zhiliaobiaoxun.com/content/278005553/b2",
        "https://www.zhiliaobiaoxun.com/content/223457459/b2",
        "https://www.zhiliaobiaoxun.com/content/177865192/b2",
        "https://www.zhiliaobiaoxun.com/content/178379112/b2",
        "https://www.zhiliaobiaoxun.com/content/224435795/b2",
        "https://www.zhiliaobiaoxun.com/content/316349674/b2",
        "https://www.zhiliaobiaoxun.com/content/245315729/b2",
        "https://www.zhiliaobiaoxun.com/content/199809129/b2",
        "https://www.zhiliaobiaoxun.com/content/397823603/b2",
        "https://www.zhiliaobiaoxun.com/content/227462285/b2",
        "https://www.zhiliaobiaoxun.com/content/213231058/b2",
        "https://www.zhiliaobiaoxun.com/content/301800044/b2",
        "https://www.zhiliaobiaoxun.com/content/301800147/b2",
        "https://www.zhiliaobiaoxun.com/content/220216565/b2"

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



