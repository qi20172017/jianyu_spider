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


    url_list = [
                'https://www.zhiliaobiaoxun.com/content/423320418/b2',
                'https://www.zhiliaobiaoxun.com/content/423113656/b2',
                'https://www.zhiliaobiaoxun.com/content/422787249/b2',
                'https://www.zhiliaobiaoxun.com/content/422766040/b2',
                'https://www.zhiliaobiaoxun.com/content/422589191/b2',
                'https://www.zhiliaobiaoxun.com/content/422630140/b2',
                'https://www.zhiliaobiaoxun.com/content/422479990/b2',
                'https://www.zhiliaobiaoxun.com/content/422489006/b2',
                'https://www.zhiliaobiaoxun.com/content/422184466/b2',
                'https://www.zhiliaobiaoxun.com/content/422090585/b2',
                'https://www.zhiliaobiaoxun.com/content/422084384/b2',
                'https://www.zhiliaobiaoxun.com/content/421806421/b2',
                'https://www.zhiliaobiaoxun.com/content/421534811/b2',
                'https://www.zhiliaobiaoxun.com/content/421534882/b2',
                'https://www.zhiliaobiaoxun.com/content/421435691/b2',
                'https://www.zhiliaobiaoxun.com/content/421394900/b2',
                'https://www.zhiliaobiaoxun.com/content/421562709/b2',
                'https://www.zhiliaobiaoxun.com/content/421090933/b2',
                'https://www.zhiliaobiaoxun.com/content/420841531/b2',
                'https://www.zhiliaobiaoxun.com/content/420657676/b2',
                'https://www.zhiliaobiaoxun.com/content/420659117/b2',
                'https://www.zhiliaobiaoxun.com/content/420689568/b2',
                'https://www.zhiliaobiaoxun.com/content/420683038/b2',
                'https://www.zhiliaobiaoxun.com/content/420659075/b2',
                'https://www.zhiliaobiaoxun.com/content/420531057/b2',
                'https://www.zhiliaobiaoxun.com/content/420693516/b2',
                'https://www.zhiliaobiaoxun.com/content/420714157/b2',
                'https://www.zhiliaobiaoxun.com/content/420351894/b2',
                'https://www.zhiliaobiaoxun.com/content/420209042/b2',
                'https://www.zhiliaobiaoxun.com/content/419599842/b2',
                'https://www.zhiliaobiaoxun.com/content/419162597/b2',
                'https://www.zhiliaobiaoxun.com/content/418971317/b2',
                'https://www.zhiliaobiaoxun.com/content/418688109/b2',
                'https://www.zhiliaobiaoxun.com/content/418417501/b2',
                'https://www.zhiliaobiaoxun.com/content/418416079/b2',
                'https://www.zhiliaobiaoxun.com/content/418198327/b2',
                'https://www.zhiliaobiaoxun.com/content/418182234/b2',
                'https://www.zhiliaobiaoxun.com/content/419787889/b2',
                'https://www.zhiliaobiaoxun.com/content/417714603/b2',
                'https://www.zhiliaobiaoxun.com/content/417714591/b2',
                'https://www.zhiliaobiaoxun.com/content/417230189/b2',
                'https://www.zhiliaobiaoxun.com/content/417153613/b2',
                'https://www.zhiliaobiaoxun.com/content/416883338/b2',
                'https://www.zhiliaobiaoxun.com/content/416078374/b2',
                'https://www.zhiliaobiaoxun.com/content/415924460/b2',
                'https://www.zhiliaobiaoxun.com/content/415968885/b2',
                'https://www.zhiliaobiaoxun.com/content/415327836/b2',
                'https://www.zhiliaobiaoxun.com/content/415339127/b2',
                'https://www.zhiliaobiaoxun.com/content/415149665/b2',
                'https://www.zhiliaobiaoxun.com/content/414401200/b2',
                'https://www.zhiliaobiaoxun.com/content/414079323/b2',
                'https://www.zhiliaobiaoxun.com/content/413887275/b2',
                'https://www.zhiliaobiaoxun.com/content/413773508/b2',
                'https://www.zhiliaobiaoxun.com/content/412043173/b2',
                'https://www.zhiliaobiaoxun.com/content/411857811/b2',
                'https://www.zhiliaobiaoxun.com/content/411890549/b2',
                'https://www.zhiliaobiaoxun.com/content/410796095/b2',
                'https://www.zhiliaobiaoxun.com/content/409097361/b2',
                'https://www.zhiliaobiaoxun.com/content/408894898/b2',
                'https://www.zhiliaobiaoxun.com/content/408612424/b2',
                'https://www.zhiliaobiaoxun.com/content/407559539/b2',
                'https://www.zhiliaobiaoxun.com/content/407501289/b2',
                'https://www.zhiliaobiaoxun.com/content/407408123/b2',
                'https://www.zhiliaobiaoxun.com/content/406342443/b2',
                'https://www.zhiliaobiaoxun.com/content/405925795/b2',
                'https://www.zhiliaobiaoxun.com/content/405871197/b2',
                'https://www.zhiliaobiaoxun.com/content/405774154/b2',
                'https://www.zhiliaobiaoxun.com/content/405691308/b2',
                'https://www.zhiliaobiaoxun.com/content/405491851/b2',
                'https://www.zhiliaobiaoxun.com/content/405246697/b2',
                'https://www.zhiliaobiaoxun.com/content/404988390/b2',
                'https://www.zhiliaobiaoxun.com/content/404768236/b2',
                'https://www.zhiliaobiaoxun.com/content/404471186/b2',
                'https://www.zhiliaobiaoxun.com/content/404373017/b2',
                'https://www.zhiliaobiaoxun.com/content/404136453/b2',
                'https://www.zhiliaobiaoxun.com/content/403815261/b2',
                'https://www.zhiliaobiaoxun.com/content/403781298/b2',
                'https://www.zhiliaobiaoxun.com/content/419870077/b2',
                'https://www.zhiliaobiaoxun.com/content/403326731/b2',
                'https://www.zhiliaobiaoxun.com/content/403323803/b2',
                'https://www.zhiliaobiaoxun.com/content/403156052/b2',
                'https://www.zhiliaobiaoxun.com/content/403169418/b2',
                'https://www.zhiliaobiaoxun.com/content/403065008/b2',
                'https://www.zhiliaobiaoxun.com/content/403027464/b2',
                'https://www.zhiliaobiaoxun.com/content/402948189/b2',
                'https://www.zhiliaobiaoxun.com/content/402649654/b2',
                'https://www.zhiliaobiaoxun.com/content/402480398/b2',
                'https://www.zhiliaobiaoxun.com/content/402295282/b2',
                'https://www.zhiliaobiaoxun.com/content/402210226/b2',
                'https://www.zhiliaobiaoxun.com/content/402130663/b2',
                'https://www.zhiliaobiaoxun.com/content/401808294/b2',
                'https://www.zhiliaobiaoxun.com/content/401316023/b2',
                'https://www.zhiliaobiaoxun.com/content/401165625/b2',
                'https://www.zhiliaobiaoxun.com/content/401165596/b2',
                'https://www.zhiliaobiaoxun.com/content/401024022/b2',
                'https://www.zhiliaobiaoxun.com/content/404990255/b2',
                'https://www.zhiliaobiaoxun.com/content/400653060/b2',
                'https://www.zhiliaobiaoxun.com/content/405144682/b2',
                'https://www.zhiliaobiaoxun.com/content/400343372/b2',
                'https://www.zhiliaobiaoxun.com/content/400288905/b2',
                'https://www.zhiliaobiaoxun.com/content/400565664/b2',
                'https://www.zhiliaobiaoxun.com/content/399895768/b2',
                'https://www.zhiliaobiaoxun.com/content/399144728/b2',
                'https://www.zhiliaobiaoxun.com/content/398915768/b2',
                'https://www.zhiliaobiaoxun.com/content/398473926/b2',
                'https://www.zhiliaobiaoxun.com/content/397892031/b2',
                'https://www.zhiliaobiaoxun.com/content/397417342/b2',
                'https://www.zhiliaobiaoxun.com/content/397445454/b2',
                'https://www.zhiliaobiaoxun.com/content/397303318/b2',
                'https://www.zhiliaobiaoxun.com/content/397319988/b2',
                'https://www.zhiliaobiaoxun.com/content/396144676/b2',
                'https://www.zhiliaobiaoxun.com/content/396119355/b2',
                'https://www.zhiliaobiaoxun.com/content/395396356/b2',
                'https://www.zhiliaobiaoxun.com/content/416632275/b2',
                'https://www.zhiliaobiaoxun.com/content/395127202/b2',
                'https://www.zhiliaobiaoxun.com/content/394040921/b2',
                'https://www.zhiliaobiaoxun.com/content/419889927/b2',
                'https://www.zhiliaobiaoxun.com/content/393905946/b2',
                'https://www.zhiliaobiaoxun.com/content/393872199/b2',
                'https://www.zhiliaobiaoxun.com/content/393468217/b2',
                'https://www.zhiliaobiaoxun.com/content/392940877/b2',
                'https://www.zhiliaobiaoxun.com/content/391942908/b2',
                'https://www.zhiliaobiaoxun.com/content/404420518/b2',
                'https://www.zhiliaobiaoxun.com/content/391793483/b2',
                'https://www.zhiliaobiaoxun.com/content/391502705/b2',
                'https://www.zhiliaobiaoxun.com/content/391273295/b2',
                'https://www.zhiliaobiaoxun.com/content/389241839/b2',
                'https://www.zhiliaobiaoxun.com/content/388478258/b2',
                'https://www.zhiliaobiaoxun.com/content/386730126/b2',
                'https://www.zhiliaobiaoxun.com/content/385949048/b2',
                'https://www.zhiliaobiaoxun.com/content/383220371/b2',
                'https://www.zhiliaobiaoxun.com/content/383208914/b2',
                'https://www.zhiliaobiaoxun.com/content/383208773/b2',
                'https://www.zhiliaobiaoxun.com/content/379472467/b2',
                'https://www.zhiliaobiaoxun.com/content/379415488/b2',
                'https://www.zhiliaobiaoxun.com/content/377111189/b2',
                'https://www.zhiliaobiaoxun.com/content/376071068/b2',
                'https://www.zhiliaobiaoxun.com/content/374492919/b2',
                'https://www.zhiliaobiaoxun.com/content/395743782/b2',
                'https://www.zhiliaobiaoxun.com/content/373806912/b2',
                'https://www.zhiliaobiaoxun.com/content/373826917/b2',
                'https://www.zhiliaobiaoxun.com/content/373832551/b2',
                'https://www.zhiliaobiaoxun.com/content/373844139/b2',
                'https://www.zhiliaobiaoxun.com/content/373509122/b2',
                'https://www.zhiliaobiaoxun.com/content/373328265/b2',
                'https://www.zhiliaobiaoxun.com/content/372263200/b2',
                'https://www.zhiliaobiaoxun.com/content/391374483/b2',
                'https://www.zhiliaobiaoxun.com/content/371065372/b2',
                'https://www.zhiliaobiaoxun.com/content/370851676/b2',
                'https://www.zhiliaobiaoxun.com/content/369545380/b2',
                'https://www.zhiliaobiaoxun.com/content/368310878/b2',
                'https://www.zhiliaobiaoxun.com/content/368210064/b2',
                'https://www.zhiliaobiaoxun.com/content/368184933/b2',
                'https://www.zhiliaobiaoxun.com/content/367784241/b2',
                'https://www.zhiliaobiaoxun.com/content/367842012/b2',
                'https://www.zhiliaobiaoxun.com/content/367667494/b2',
                'https://www.zhiliaobiaoxun.com/content/367689754/b2',
                'https://www.zhiliaobiaoxun.com/content/376229278/b2',
                'https://www.zhiliaobiaoxun.com/content/367454730/b2',
                'https://www.zhiliaobiaoxun.com/content/367400904/b2',
                'https://www.zhiliaobiaoxun.com/content/367287087/b2',
                'https://www.zhiliaobiaoxun.com/content/367253314/b2',
                'https://www.zhiliaobiaoxun.com/content/366931558/b2',
                'https://www.zhiliaobiaoxun.com/content/366535776/b2',
                'https://www.zhiliaobiaoxun.com/content/366330118/b2',
                'https://www.zhiliaobiaoxun.com/content/366435687/b2',
                'https://www.zhiliaobiaoxun.com/content/366014818/b2',
                'https://www.zhiliaobiaoxun.com/content/366041651/b2',
                'https://www.zhiliaobiaoxun.com/content/395366957/b2',
                'https://www.zhiliaobiaoxun.com/content/365948309/b2',
                'https://www.zhiliaobiaoxun.com/content/365700046/b2',
                'https://www.zhiliaobiaoxun.com/content/364136438/b2',
                'https://www.zhiliaobiaoxun.com/content/363648694/b2',
                'https://www.zhiliaobiaoxun.com/content/363144252/b2',
                'https://www.zhiliaobiaoxun.com/content/362335911/b2',
                'https://www.zhiliaobiaoxun.com/content/361999622/b2',
                'https://www.zhiliaobiaoxun.com/content/361983680/b2',
                'https://www.zhiliaobiaoxun.com/content/362024611/b2',
                'https://www.zhiliaobiaoxun.com/content/361360768/b2',
                'https://www.zhiliaobiaoxun.com/content/361309039/b2',
                'https://www.zhiliaobiaoxun.com/content/360999459/b2',
                'https://www.zhiliaobiaoxun.com/content/359421821/b2',
                'https://www.zhiliaobiaoxun.com/content/359018665/b2',
                'https://www.zhiliaobiaoxun.com/content/355601309/b2',
                'https://www.zhiliaobiaoxun.com/content/355274502/b2',
                'https://www.zhiliaobiaoxun.com/content/355029129/b2',
                'https://www.zhiliaobiaoxun.com/content/355029143/b2',
                'https://www.zhiliaobiaoxun.com/content/352571664/b2',
                'https://www.zhiliaobiaoxun.com/content/352549981/b2',
                'https://www.zhiliaobiaoxun.com/content/351557099/b2',
                'https://www.zhiliaobiaoxun.com/content/389241677/b2',
                'https://www.zhiliaobiaoxun.com/content/351541965/b2',
                'https://www.zhiliaobiaoxun.com/content/351054185/b2',
                'https://www.zhiliaobiaoxun.com/content/351289491/b2',
                'https://www.zhiliaobiaoxun.com/content/346760739/b2',
                'https://www.zhiliaobiaoxun.com/content/345728700/b2',
                'https://www.zhiliaobiaoxun.com/content/344814497/b2',
                'https://www.zhiliaobiaoxun.com/content/332838472/b2',
                'https://www.zhiliaobiaoxun.com/content/344009851/b2',
                'https://www.zhiliaobiaoxun.com/content/343284273/b2',
                'https://www.zhiliaobiaoxun.com/content/343320451/b2',
                'https://www.zhiliaobiaoxun.com/content/342609728/b2',
                'https://www.zhiliaobiaoxun.com/content/341133510/b2',
                'https://www.zhiliaobiaoxun.com/content/339096628/b2',
                'https://www.zhiliaobiaoxun.com/content/338176219/b2',
                'https://www.zhiliaobiaoxun.com/content/337912652/b2',
                'https://www.zhiliaobiaoxun.com/content/337295330/b2',
                'https://www.zhiliaobiaoxun.com/content/335301314/b2',
                'https://www.zhiliaobiaoxun.com/content/334081293/b2',
                'https://www.zhiliaobiaoxun.com/content/333420302/b2',
                'https://www.zhiliaobiaoxun.com/content/332579185/b2',
                'https://www.zhiliaobiaoxun.com/content/352450488/b2',
                'https://www.zhiliaobiaoxun.com/content/332089447/b2',
                'https://www.zhiliaobiaoxun.com/content/332124930/b2',
                'https://www.zhiliaobiaoxun.com/content/329978686/b2',
                'https://www.zhiliaobiaoxun.com/content/328695658/b2',
                'https://www.zhiliaobiaoxun.com/content/328109397/b2',
                'https://www.zhiliaobiaoxun.com/content/327878525/b2',
                'https://www.zhiliaobiaoxun.com/content/327294998/b2',
                'https://www.zhiliaobiaoxun.com/content/327014442/b2',
                'https://www.zhiliaobiaoxun.com/content/326407508/b2',
                'https://www.zhiliaobiaoxun.com/content/326356236/b2',
                'https://www.zhiliaobiaoxun.com/content/326464568/b2',
                'https://www.zhiliaobiaoxun.com/content/325985517/b2',
                'https://www.zhiliaobiaoxun.com/content/325714449/b2',
                'https://www.zhiliaobiaoxun.com/content/324700390/b2',
                'https://www.zhiliaobiaoxun.com/content/323866644/b2',
                'https://www.zhiliaobiaoxun.com/content/322775292/b2',
                'https://www.zhiliaobiaoxun.com/content/330720855/b2',
                'https://www.zhiliaobiaoxun.com/content/316940779/b2',
                'https://www.zhiliaobiaoxun.com/content/311652307/b2',
                'https://www.zhiliaobiaoxun.com/content/307453301/b2',
                'https://www.zhiliaobiaoxun.com/content/306927784/b2',
                'https://www.zhiliaobiaoxun.com/content/307233633/b2',
                'https://www.zhiliaobiaoxun.com/content/307247244/b2',
                'https://www.zhiliaobiaoxun.com/content/295391694/b2',
                'https://www.zhiliaobiaoxun.com/content/354893351/b2',
                'https://www.zhiliaobiaoxun.com/content/299574828/b2',
                'https://www.zhiliaobiaoxun.com/content/286007505/b2',
                'https://www.zhiliaobiaoxun.com/content/416174801/b2',
                'https://www.zhiliaobiaoxun.com/content/337640934/b2',
                'https://www.zhiliaobiaoxun.com/content/260412073/b2',
                'https://www.zhiliaobiaoxun.com/content/321763443/b2',
                'https://www.zhiliaobiaoxun.com/content/291019231/b2',
                'https://www.zhiliaobiaoxun.com/content/320684025/b2',
                'https://www.zhiliaobiaoxun.com/content/320166510/b2',
                'https://www.zhiliaobiaoxun.com/content/316675641/b2',
                'https://www.zhiliaobiaoxun.com/content/313127406/b2',
                'https://www.zhiliaobiaoxun.com/content/310887786/b2',
                'https://www.zhiliaobiaoxun.com/content/308546398/b2',
                'https://www.zhiliaobiaoxun.com/content/308357178/b2',
                'https://www.zhiliaobiaoxun.com/content/292428029/b2',
                'https://www.zhiliaobiaoxun.com/content/306554602/b2',
                'https://www.zhiliaobiaoxun.com/content/289652722/b2',
                'https://www.zhiliaobiaoxun.com/content/307578316/b2',
                'https://www.zhiliaobiaoxun.com/content/288004316/b2',
                'https://www.zhiliaobiaoxun.com/content/321226349/b2',
                'https://www.zhiliaobiaoxun.com/content/285799232/b2',
                'https://www.zhiliaobiaoxun.com/content/284842506/b2',
                'https://www.zhiliaobiaoxun.com/content/284014969/b2',
                'https://www.zhiliaobiaoxun.com/content/321226978/b2',
                'https://www.zhiliaobiaoxun.com/content/313653288/b2',
                'https://www.zhiliaobiaoxun.com/content/282895607/b2',
                'https://www.zhiliaobiaoxun.com/content/307360764/b2',
                'https://www.zhiliaobiaoxun.com/content/330048354/b2',
                'https://www.zhiliaobiaoxun.com/content/307364580/b2',
                'https://www.zhiliaobiaoxun.com/content/288591699/b2',
                'https://www.zhiliaobiaoxun.com/content/288605315/b2',
                'https://www.zhiliaobiaoxun.com/content/307364741/b2',
                'https://www.zhiliaobiaoxun.com/content/335460960/b2',
                'https://www.zhiliaobiaoxun.com/content/291311313/b2',
                'https://www.zhiliaobiaoxun.com/content/292785442/b2',
                'https://www.zhiliaobiaoxun.com/content/352836655/b2',
                'https://www.zhiliaobiaoxun.com/content/306793243/b2',
                'https://www.zhiliaobiaoxun.com/content/322911007/b2',
                'https://www.zhiliaobiaoxun.com/content/334218871/b2',
                'https://www.zhiliaobiaoxun.com/content/313667154/b2',
                'https://www.zhiliaobiaoxun.com/content/291733049/b2',
                'https://www.zhiliaobiaoxun.com/content/374322986/b2',
                'https://www.zhiliaobiaoxun.com/content/352838450/b2',
                'https://www.zhiliaobiaoxun.com/content/306797097/b2',
                'https://www.zhiliaobiaoxun.com/content/321228762/b2',
                'https://www.zhiliaobiaoxun.com/content/307394450/b2',
                'https://www.zhiliaobiaoxun.com/content/360751226/b2',
                'https://www.zhiliaobiaoxun.com/content/417544363/b2',
                'https://www.zhiliaobiaoxun.com/content/291735935/b2',
                'https://www.zhiliaobiaoxun.com/content/258488704/b2',
                'https://www.zhiliaobiaoxun.com/content/313668934/b2',
                'https://www.zhiliaobiaoxun.com/content/276092741/b2',
                'https://www.zhiliaobiaoxun.com/content/253281597/b2',
                'https://www.zhiliaobiaoxun.com/content/307391728/b2',
                'https://www.zhiliaobiaoxun.com/content/316339547/b2',
                'https://www.zhiliaobiaoxun.com/content/285810559/b2',
                'https://www.zhiliaobiaoxun.com/content/316968431/b2',
                'https://www.zhiliaobiaoxun.com/content/285840241/b2',
                'https://www.zhiliaobiaoxun.com/content/245234612/b2',
                'https://www.zhiliaobiaoxun.com/content/313674578/b2',
                'https://www.zhiliaobiaoxun.com/content/238739313/b2',
                'https://www.zhiliaobiaoxun.com/content/272492398/b2',
                'https://www.zhiliaobiaoxun.com/content/307588295/b2',
                'https://www.zhiliaobiaoxun.com/content/306749042/b2',
                'https://www.zhiliaobiaoxun.com/content/313703220/b2',
                'https://www.zhiliaobiaoxun.com/content/421832255/b2',
                'https://www.zhiliaobiaoxun.com/content/284096494/b2',
                'https://www.zhiliaobiaoxun.com/content/181269957/b2',
                'https://www.zhiliaobiaoxun.com/content/313720859/b2',
                'https://www.zhiliaobiaoxun.com/content/416004029/b2',
                'https://www.zhiliaobiaoxun.com/content/313683106/b2',
                'https://www.zhiliaobiaoxun.com/content/175193961/b2',
                'https://www.zhiliaobiaoxun.com/content/334219514/b2',
                'https://www.zhiliaobiaoxun.com/content/319784194/b2',
                'https://www.zhiliaobiaoxun.com/content/263986262/b2',
                'https://www.zhiliaobiaoxun.com/content/289516053/b2',
                'https://www.zhiliaobiaoxun.com/content/328593896/b2',
                'https://www.zhiliaobiaoxun.com/content/323185212/b2',
                'https://www.zhiliaobiaoxun.com/content/223293751/b2',
                'https://www.zhiliaobiaoxun.com/content/364741697/b2',
                'https://www.zhiliaobiaoxun.com/content/322594657/b2',
                'https://www.zhiliaobiaoxun.com/content/324053301/b2',
                'https://www.zhiliaobiaoxun.com/content/307597396/b2',
                'https://www.zhiliaobiaoxun.com/content/291381234/b2',
                'https://www.zhiliaobiaoxun.com/content/210928882/b2',
                'https://www.zhiliaobiaoxun.com/content/408712538/b2',
                'https://www.zhiliaobiaoxun.com/content/409539679/b2',
                'https://www.zhiliaobiaoxun.com/content/307337452/b2',
                'https://www.zhiliaobiaoxun.com/content/290017955/b2',
                'https://www.zhiliaobiaoxun.com/content/407025451/b2',
                'https://www.zhiliaobiaoxun.com/content/305200089/b2',
                'https://www.zhiliaobiaoxun.com/content/306036381/b2',
                'https://www.zhiliaobiaoxun.com/content/313892596/b2',
                'https://www.zhiliaobiaoxun.com/content/289673693/b2',
                'https://www.zhiliaobiaoxun.com/content/207443083/b2',
                'https://www.zhiliaobiaoxun.com/content/306834240/b2',
                'https://www.zhiliaobiaoxun.com/content/272493663/b2',
                'https://www.zhiliaobiaoxun.com/content/266318741/b2',
                'https://www.zhiliaobiaoxun.com/content/311184710/b2',
                'https://www.zhiliaobiaoxun.com/content/364882314/b2',
                'https://www.zhiliaobiaoxun.com/content/288407365/b2',
                'https://www.zhiliaobiaoxun.com/content/289695266/b2',
                'https://www.zhiliaobiaoxun.com/content/271117914/b2',
                'https://www.zhiliaobiaoxun.com/content/279661540/b2',
                'https://www.zhiliaobiaoxun.com/content/422927415/b2',
                'https://www.zhiliaobiaoxun.com/content/292585447/b2',
                'https://www.zhiliaobiaoxun.com/content/292584651/b2',
                'https://www.zhiliaobiaoxun.com/content/293159973/b2',
                'https://www.zhiliaobiaoxun.com/content/206567179/b2',
                'https://www.zhiliaobiaoxun.com/content/206568602/b2',
                'https://www.zhiliaobiaoxun.com/content/232973494/b2',
                'https://www.zhiliaobiaoxun.com/content/306857776/b2',
                'https://www.zhiliaobiaoxun.com/content/306858090/b2',
                'https://www.zhiliaobiaoxun.com/content/271121278/b2',
                'https://www.zhiliaobiaoxun.com/content/258460673/b2',
                'https://www.zhiliaobiaoxun.com/content/307609507/b2',
                'https://www.zhiliaobiaoxun.com/content/271122336/b2',
                'https://www.zhiliaobiaoxun.com/content/307609874/b2',
                'https://www.zhiliaobiaoxun.com/content/421935864/b2',
                'https://www.zhiliaobiaoxun.com/content/411031905/b2',
                'https://www.zhiliaobiaoxun.com/content/287936647/b2',
                'https://www.zhiliaobiaoxun.com/content/409636129/b2',
                'https://www.zhiliaobiaoxun.com/content/287948639/b2',
                'https://www.zhiliaobiaoxun.com/content/311695362/b2',
                'https://www.zhiliaobiaoxun.com/content/311696477/b2',
                'https://www.zhiliaobiaoxun.com/content/306892932/b2',
                'https://www.zhiliaobiaoxun.com/content/290021012/b2',
                'https://www.zhiliaobiaoxun.com/content/202812664/b2',
                'https://www.zhiliaobiaoxun.com/content/177140914/b2',
                'https://www.zhiliaobiaoxun.com/content/410685113/b2',
                'https://www.zhiliaobiaoxun.com/content/306036744/b2',
                'https://www.zhiliaobiaoxun.com/content/202746447/b2',
                'https://www.zhiliaobiaoxun.com/content/217932893/b2',
                'https://www.zhiliaobiaoxun.com/content/202230244/b2',
                'https://www.zhiliaobiaoxun.com/content/307620032/b2',
                'https://www.zhiliaobiaoxun.com/content/167279990/b2',
                'https://www.zhiliaobiaoxun.com/content/402707797/b2',
                'https://www.zhiliaobiaoxun.com/content/412090622/b2',
                'https://www.zhiliaobiaoxun.com/content/303645514/b2',
                'https://www.zhiliaobiaoxun.com/content/179597132/b2',
                'https://www.zhiliaobiaoxun.com/content/216953055/b2',
                'https://www.zhiliaobiaoxun.com/content/414553783/b2',
                'https://www.zhiliaobiaoxun.com/content/289923298/b2',
                'https://www.zhiliaobiaoxun.com/content/411502387/b2',
                'https://www.zhiliaobiaoxun.com/content/179037300/b2',
                'https://www.zhiliaobiaoxun.com/content/306929222/b2',
                'https://www.zhiliaobiaoxun.com/content/213698390/b2',
                'https://www.zhiliaobiaoxun.com/content/202267468/b2',
                'https://www.zhiliaobiaoxun.com/content/306948326/b2',
                'https://www.zhiliaobiaoxun.com/content/325482820/b2',
                'https://www.zhiliaobiaoxun.com/content/409571290/b2',
                'https://www.zhiliaobiaoxun.com/content/413372751/b2',
                'https://www.zhiliaobiaoxun.com/content/324556112/b2',
                'https://www.zhiliaobiaoxun.com/content/395223414/b2',
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



