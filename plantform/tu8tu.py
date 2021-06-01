import requests
import re
import json
import ssl
from common.tools import safe_get, time_exchange, random_sleep
from model.msql.my_dao.my_tu_dao import MyTuDao
from model.pg.pg_dao.pg_tu_dao import PgTuDao
from app.moen_app import moenApp
from plantform.weapon import *
from model.rds import rds_100_2

ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()
TYPE_IDCT = {
    "beautyChart": "美图",
    "companyCase": "案例",  # 暂且拿不到
    "diary": "日记",
    "ugcArticle": "文章",
    "ugcAsk": "问答"
}


@moenApp.task(
    name='moen.tu8tu.list',
    bind=True,
    acks_late=True,
    rate_limit='10/m',
    # autoretry_for=(HttpError, TypeError, WeiXinError, TError),
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def tu8tu(self, page, key_word):
    url = "https://apigwc2.huhudi.com/cgi/multi/search?uid=16864430&ticket=HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar&source=tbt-app&accountId=24365073"

    payload = {
        "args": {
            "pubArgs": "{\"channel\":\"小米\",\"appversion\":\"8.17.3\",\"systemversion\":\"25\",\"apkPackageName\":\"com.to8to.housekeeper\",\"appid\":\"15\",\"version\":\"2.5\",\"appostype\":\"1\",\"appversioncode\":\"91730\",\"cityName\":\"上海\",\"deviceModel\":\"sailfish-Pixel\",\"device\":\"google-Pixel\",\"first_id\":\"633540b26c1363ba493fb03c9b0641a1\",\"isnew\":\"1\",\"imei\":\"633540b26c1363ba493fb03c9b0641a1\",\"cityId\":\"1103\",\"cityid\":\"1103\",\"t8t_device_id\":\"633540b26c1363ba493fb03c9b0641a1\",\"uid\":\"16864430\",\"ticket\":\"HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar\",\"to8to_token\":\"HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar\",\"accountId\":\"24365073\"}",
            "uid": "16864430",
            "scope": "0",
            "edition": 3,
            "page": page,
            "keyWord": key_word,
            "subScope": "1",
            "perPage": 20
        }
    }

    headers = {
        'device': 'google-Pixel',
        'isnew': '1',
        'apkPackageName': 'com.to8to.housekeeper',
        'cityid': '1103',
        'appid': '15',
        'ticket': 'HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar',
        'cityName': '%%E4%%B8%%8A%%E6%%B5%%B7',
        'to8to_token': 'HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar',
        'first_id': '633540b26c1363ba493fb03c9b0641a1',
        't8t_device_id': '633540b26c1363ba493fb03c9b0641a1',
        'appversioncode': '91730',
        'imei': '633540b26c1363ba493fb03c9b0641a1',
        'systemversion': '25',
        'appversion': '8.17.3',
        'appostype': '1',
        'accountId': '24365073',
        'version': '2.5',
        'uid': '16864430',
        'deviceModel': 'sailfish-Pixel',
        'channel': '%%E5%%B0%%8F%%E7%%B1%%B3',
        'cityId': '1103',
        'User-Agent': 'to8to_andr/8.17.3 (google;Pixel;Android 7.1.2) channel/%%E5%%B0%%8F%%E7%%B1%%B3',
        'referer': 'https://to8to.com',
        'Content-Type': 'application/json; charset=utf-8',
        'Host': 'apigwc2.huhudi.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    response = requests.request("POST", url, headers=headers, json=payload, verify=False)
    raw_data = response.text
    # print(response.text)
    if raw_data:
        raw_data = json.loads(raw_data)
        article_list = raw_data["result"]["commonFeedVos"]
        total = safe_get(raw_data, "result", "total")

        send_next_page(total, page, key_word)
        save_page("tu8tu", key_word, page)

        for article in article_list:
            result_data = {}

            # print(article)
            result_data["brand"] = key_word
            result_data["title"] = safe_get(article, "cover", "title")
            result_data["nickname"] = safe_get(article, "bottom", "title")
            result_data["item_type"] = safe_get(article, "interaction", "moduleCode")
            result_data["item_id"] = str(safe_get(article, "content", "id")) if safe_get(article, "content",
                                                                                         "id") else safe_get(article,
                                                                                                             "content",
                                                                                                             "id")
            result_data["router"] = safe_get(article, "content", "router")
            result_data["share_url"] = safe_get(article, "content", "shareUrl")

            if result_data["item_id"]:
                print(result_data)
                PgTuDao.upsert(**result_data)
                if result_data["item_type"] == "beautyChart":
                    # tu8tu_picture(result_data)

                    moenApp.send_task("moen.tu8tu.picture", args=(result_data,))

                elif result_data["item_type"] == "diary":
                    if result_data["router"]:
                        local_id = re.findall('localeid=(.*?)&di', result_data["router"])
                        if local_id:
                            result_data["item_id"] = local_id[0]
                            # tu8tu_diary(result_data)
                            moenApp.send_task("moen.tu8tu.diary", args=(result_data,))
                elif result_data["item_type"] == "ugcArticle":
                    # tu8tu_article(result_data)
                    moenApp.send_task("moen.tu8tu.article", args=(result_data,))

                elif result_data["item_type"] == "ugcAsk":
                    # tu8tu_question(result_data)
                    moenApp.send_task("moen.tu8tu.question", args=(result_data,))

            print("-------Muto-------")



@moenApp.task(
    name='moen.tu8tu.picture',
    bind=True,
    acks_late=True,
    rate_limit='10/m',
    # autoretry_for=(HttpError, TypeError, WeiXinError, TError),
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def tu8tu_picture(self, item_data):
    random_sleep(1,5)
    if item_data:
        item_id = item_data["item_id"]
    else:
        return

    url = "https://apigwc2.huhudi.com/cgi/efp/xiaoguotu/app/detail/v2?uid=16864430&ticket=HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar&source=tbt-app&accountId=24365073"

    payload = f"args=%7B%22pubArgs%22%3A%22%7B%5C%22channel%5C%22%3A%5C%22%E5%B0%8F%E7%B1%B3%5C%22%2C%5C%22appversion%5C%22%3A%5C%228.17.3%5C%22%2C%5C%22systemversion%5C%22%3A%5C%2225%5C%22%2C%5C%22apkPackageName%5C%22%3A%5C%22com.to8to.housekeeper%5C%22%2C%5C%22appid%5C%22%3A%5C%2215%5C%22%2C%5C%22version%5C%22%3A%5C%222.5%5C%22%2C%5C%22appostype%5C%22%3A%5C%221%5C%22%2C%5C%22appversioncode%5C%22%3A%5C%2291730%5C%22%2C%5C%22cityName%5C%22%3A%5C%22%E4%B8%8A%E6%B5%B7%5C%22%2C%5C%22deviceModel%5C%22%3A%5C%22sailfish-Pixel%5C%22%2C%5C%22device%5C%22%3A%5C%22google-Pixel%5C%22%2C%5C%22first_id%5C%22%3A%5C%22633540b26c1363ba493fb03c9b0641a1%5C%22%2C%5C%22isnew%5C%22%3A%5C%221%5C%22%2C%5C%22imei%5C%22%3A%5C%22633540b26c1363ba493fb03c9b0641a1%5C%22%2C%5C%22cityId%5C%22%3A%5C%221103%5C%22%2C%5C%22cityid%5C%22%3A%5C%221103%5C%22%2C%5C%22t8t_device_id%5C%22%3A%5C%22633540b26c1363ba493fb03c9b0641a1%5C%22%2C%5C%22uid%5C%22%3A%5C%2216864430%5C%22%2C%5C%22ticket%5C%22%3A%5C%22HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar%5C%22%2C%5C%22to8to_token%5C%22%3A%5C%22HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar%5C%22%2C%5C%22accountId%5C%22%3A%5C%2224365073%5C%22%7D%22%2C%22oldaid%22%3A{item_id}%2C%22slideCount%22%3A1%7D"

    headers = {
        'device': 'google-Pixel',
        'isnew': '1',
        'apkpackagename': 'com.to8to.housekeeper',
        'cityid': '1103',
        'appid': '15',
        'ticket': 'HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar',
        'cityname': '%E4%B8%8A%E6%B5%B7',
        'to8to_token': 'HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar',
        'first_id': '633540b26c1363ba493fb03c9b0641a1',
        't8t_device_id': '633540b26c1363ba493fb03c9b0641a1',
        'appversioncode': '91730',
        'imei': '633540b26c1363ba493fb03c9b0641a1',
        'systemversion': '25',
        'appversion': '8.17.3',
        'appostype': '1',
        'accountid': '24365073',
        'version': '2.5',
        'uid': '16864430',
        'devicemodel': 'sailfish-Pixel',
        'channel': '%E5%B0%8F%E7%B1%B3',
        'user-agent': 'to8to_andr/8.17.3 (google;Pixel;Android 7.1.2) channel/%E5%B0%8F%E7%B1%B3',
        'referer': 'https://to8to.com',
        'content-type': 'application/x-www-form-urlencoded',
        'content-length': '1369',
        'accept-encoding': 'gzip',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    raw_data = response.text
    if raw_data:
        raw_data = json.loads(raw_data)

        print(response.text)
        result = raw_data.get("result")
        if result:
            item_data["create_time"] = result.get("sourceCreateTime")
            if item_data["create_time"] and item_data["create_time"] != 0:
                save_time(item_data["brand"], item_data["create_time"])       # 更新一下时间
                item_data["create_time"] = time_exchange(item_data["create_time"])
            else:
                item_data["create_time"] = None

            detailPic = result.get("detailPic")
            if detailPic:
                item_data["collect_num"] = detailPic[0]["collectNum"]
                item_data["praise_num"] = detailPic[0]["praiseNum"]
                item_data["comment_num"] = detailPic[0]["commentNum"]
                item_data["pic_url"] = detailPic[0]["picPath"]
            item_data["content"] = result.get("desc")
            item_data["author_avatar"] = result.get("authorAvatar")
            item_data["author_id"] = str(result.get("authorId")) if result.get("authorId") else None

            if item_data["item_id"]:
                # MyTuDao.upsert(**item_data)

                print(item_data)
                PgTuDao.upsert(**item_data)


@moenApp.task(
    name='moen.tu8tu.article',
    bind=True,
    acks_late=True,
    rate_limit='10/m',
    # autoretry_for=(HttpError, TypeError, WeiXinError, TError),
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def tu8tu_article(self, item_data):
    random_sleep(1,5)

    if item_data:
        item_id = item_data["item_id"]
    else:
        return

    url = f"https://appapi.huhudi.com/social/article/detail?device=google-Pixel&isnew=0&apkPackageName=com.to8to.housekeeper&cityid=1103&appid=15&cityName=%E4%B8%8A%E6%B5%B7&ticket=HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar&to8to_token=HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar&first_id=633540b26c1363ba493fb03c9b0641a1&t8t_device_id=633540b26c1363ba493fb03c9b0641a1&appversioncode=91730&systemversion=25&imei=633540b26c1363ba493fb03c9b0641a1&id={item_id}&appversion=8.17.3&appostype=1&accountId=24365073&version=2.5&deviceModel=sailfish-Pixel&uid=16864430&channel=%E5%B0%8F%E7%B1%B3&cityId=1103"

    payload = {}
    headers = {
        'user-agent': 'to8to_andr/8.17.3 (google;Pixel;Android 7.1.2) channel/%E5%B0%8F%E7%B1%B3',
        'referer': 'https://to8to.com',
        'accept-encoding': 'gzip',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)

    print(response.text)
    raw_data = response.text
    if raw_data:
        raw_data = json.loads(raw_data)

        print(response.text)
        result = raw_data.get("data")
        if result:
            item_data["create_time"] = result.get("sourceCreateTime")
            if item_data["create_time"] and item_data["create_time"] != 0:
                save_time(item_data["brand"], item_data["create_time"])       # 更新一下时间
                item_data["create_time"] = time_exchange(item_data["create_time"])
            else:
                item_data["create_time"] = None

            item_data["collect_num"] = result["collectNum"]
            item_data["praise_num"] = result["praiseNum"]
            item_data["comment_num"] = result["commentNum"]
            # item_data["pic_url"] = detailPic[0]["picPath"]

            item_data["content"] = result.get("shareContent")
            item_data["long_content"] = result.get("content")

            item_data["author_avatar"] = result.get("authorAvatar")
            item_data["author_id"] = str(result.get("authorId")) if result.get("authorId") else None

            if item_data["item_id"]:
                # MyTuDao.upsert(**item_data)

                print(item_data)
                PgTuDao.upsert(**item_data)

@moenApp.task(
    name='moen.tu8tu.diary',
    bind=True,
    acks_late=True,
    rate_limit='24/m',
    # autoretry_for=(HttpError, TypeError, WeiXinError, TError),
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def tu8tu_diary(self, item_data):
    # random_sleep(1,5)

    if item_data:
        item_id = item_data["item_id"]
    else:
        return

    url = "https://apigwc2.huhudi.com/cgi/views/diarybook/app/detail?uid=16864430&ticket=HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar&source=tbt-app&accountId=24365073"

    payload = f"args=%7B%22pubArgs%22%3A%22%7B%5C%22channel%5C%22%3A%5C%22%E5%B0%8F%E7%B1%B3%5C%22%2C%5C%22appversion%5C%22%3A%5C%228.17.3%5C%22%2C%5C%22systemversion%5C%22%3A%5C%2225%5C%22%2C%5C%22apkPackageName%5C%22%3A%5C%22com.to8to.housekeeper%5C%22%2C%5C%22appid%5C%22%3A%5C%2215%5C%22%2C%5C%22version%5C%22%3A%5C%222.5%5C%22%2C%5C%22appostype%5C%22%3A%5C%221%5C%22%2C%5C%22appversioncode%5C%22%3A%5C%2291730%5C%22%2C%5C%22cityName%5C%22%3A%5C%22%E4%B8%8A%E6%B5%B7%5C%22%2C%5C%22deviceModel%5C%22%3A%5C%22sailfish-Pixel%5C%22%2C%5C%22device%5C%22%3A%5C%22google-Pixel%5C%22%2C%5C%22first_id%5C%22%3A%5C%22633540b26c1363ba493fb03c9b0641a1%5C%22%2C%5C%22isnew%5C%22%3A%5C%220%5C%22%2C%5C%22uid%5C%22%3A%5C%2216864430%5C%22%2C%5C%22ticket%5C%22%3A%5C%22HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar%5C%22%2C%5C%22to8to_token%5C%22%3A%5C%22HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar%5C%22%2C%5C%22accountId%5C%22%3A%5C%2224365073%5C%22%2C%5C%22cityId%5C%22%3A%5C%221103%5C%22%2C%5C%22cityid%5C%22%3A%5C%221103%5C%22%2C%5C%22imei%5C%22%3A%5C%22633540b26c1363ba493fb03c9b0641a1%5C%22%2C%5C%22t8t_device_id%5C%22%3A%5C%22633540b26c1363ba493fb03c9b0641a1%5C%22%7D%22%2C%22id%22%3A%22{item_id}%22%7D"
    headers = {
        'device': 'google-Pixel',
        'isnew': '0',
        'apkpackagename': 'com.to8to.housekeeper',
        'cityid': '1103',
        'appid': '15',
        'ticket': 'HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar',
        'cityname': '%E4%B8%8A%E6%B5%B7',
        'to8to_token': 'HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar',
        'first_id': '633540b26c1363ba493fb03c9b0641a1',
        't8t_device_id': '633540b26c1363ba493fb03c9b0641a1',
        'appversioncode': '91730',
        'imei': '633540b26c1363ba493fb03c9b0641a1',
        'systemversion': '25',
        'appversion': '8.17.3',
        'appostype': '1',
        'accountid': '24365073',
        'version': '2.5',
        'uid': '16864430',
        'devicemodel': 'sailfish-Pixel',
        'channel': '%E5%B0%8F%E7%B1%B3',
        'user-agent': 'to8to_andr/8.17.3 (google;Pixel;Android 7.1.2) channel/%E5%B0%8F%E7%B1%B3',
        'referer': 'https://to8to.com',
        'content-type': 'application/x-www-form-urlencoded',
        'content-length': '1347',
        'accept-encoding': 'gzip',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    print(response.text)

    raw_data = response.text
    if raw_data:
        raw_data = json.loads(raw_data)

        result = raw_data.get("result")
        if result:
            book_info = result.get("bookInfo")
            if book_info:
                item_data["area"] = book_info.get("area")
                item_data["product_sum"] = book_info.get("productSum")
                item_data["house_type"] = book_info.get("houseTypeName")
                item_data["style"] = book_info.get("styleName")
                item_data["title"] = book_info.get("title")
                item_data["cover_url"] = book_info.get("coverUrl")
                item_data["city_name"] = book_info.get("cityName")
                item_data["budget"] = book_info.get("budget")
                item_data["create_time"] = book_info.get("lastUpdateTime")
                if item_data["create_time"] and item_data["create_time"] != 0 and item_data["create_time"] != "0":
                    save_time(item_data["brand"], item_data["create_time"])  # 更新一下时间
                    item_data["create_time"] = time_exchange(int(item_data["create_time"]))
                else:
                    item_data["create_time"] = None
            user_info = result.get("userInfo")
            if user_info:
                item_data["author_avatar"] = user_info.get("authorAvatar")
                item_data["author_id"] = str(user_info.get("accountId")) if user_info.get("accountId") else None
            diary_infos = result.get("diaryInfos")
            if diary_infos:
                for diary in diary_infos:
                    item_data["collect_num"] = diary["collectNum"]
                    item_data["praise_num"] = diary["praiseNum"]
                    item_data["comment_num"] = diary["commentNum"]
                    item_data["content"] = diary.get("content")
                    images = diary.get("images")
                    if images:
                        sum_url = ""
                        for image in images:
                            if image.get("imageUrl"):
                                sum_url = sum_url + image.get("imageUrl") + "||"
                            img_create_time = image.get("updateTime")
                            if img_create_time and img_create_time != 0 and img_create_time != "0":
                                item_data["create_time"] = time_exchange(int(img_create_time))
                            else:
                                pass
                        item_data["pic_url"] = sum_url
                    else:
                        item_data["pic_url"] = None

                    comments = diary.get("comments")
                    if comments:
                        sum_com = ""
                        for comment in comments:
                            if comment.get("content"):
                                sum_com = sum_com + comment.get("content") + "<||>"
                            item_data["comment"] = sum_com
                    else:
                        item_data["comment"] = None

                    first_stage_name = diary.get("firstStageName", "")
                    second_stage_name = diary.get("secondStageName", "")

                    item_data["stage_name"] = first_stage_name + "|" + second_stage_name

                    item_data["item_id"] = str(diary.get("id")) if diary.get("id") else None

                    if item_data["item_id"]:
                        # MyTuDao.upsert(**item_data)

                        print(item_data)
                        PgTuDao.upsert(**item_data)
                    print('------Muto-----------------------')
        else:
            print("没有result")
    else:
        print("最外层，无")



@moenApp.task(
    name='moen.tu8tu.question',
    bind=True,
    acks_late=True,
    rate_limit='10/m',
    # autoretry_for=(HttpError, TypeError, WeiXinError, TError),
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def tu8tu_question(self, item_data):
    random_sleep(1,5)

    if item_data:
        item_id = item_data["item_id"]
    else:
        return

    url = "https://apigwc2.to8to.com/cgi/ask/info/data?source=tbt-app"

    payload = {"askId":item_id,"accountId":24365073,"uid":16864430}
    headers = {
        'content-length': '51',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'origin': 'https://mapp.to8to.com',
        'user-agent': 'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/N2G47O; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045614 Mobile Safari/537.36 to8to_andr/8.17.3 (google;Pixel;Android 7.1.2) channel/%E5%B0%8F%E7%B1%B3',
        'sec-fetch-mode': 'cors',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'com.to8to.housekeeper',
        'sec-fetch-site': 'same-site',
        'referer': 'https://mapp.to8to.com/ask/info/30295?channel=%E5%B0%8F%E7%B1%B3&appversion=8.17.3&systemversion=25&appid=15&version=2.5&appostype=1&appversioncode=91730&cityName=%E4%B8%8A%E6%B5%B7&device=google-Pixel&first_id=633540b26c1363ba493fb03c9b0641a1&isnew=0&uid=16864430&ticket=HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar&to8to_token=HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar&accountId=24365073&cityId=1103&cityid=1103&imei=633540b26c1363ba493fb03c9b0641a1&t8t_device_id=633540b26c1363ba493fb03c9b0641a1&pro_sourceid=104&pro_s_sourceid=101&withalipay=0',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    response = requests.request("POST", url, headers=headers, json=payload, verify=False)

    print(response.text)
    raw_data = response.text
    if raw_data:
        raw_data = json.loads(raw_data)

        print(response.text)
        result = raw_data.get("result")
        if result:
            if result.get("createTime"):
                item_data["create_time"] = result["createTime"]
            else:
                item_data["create_time"] = None

            item_data["collect_num"] = result.get("collectNum")
            item_data["praise_num"] = result.get("praiseNum")
            item_data["comment_num"] = result.get("answerNums")

            item_data["content"] = result.get("subject")
            item_data["style"] = result.get("typeName")

            item_data["author_avatar"] = result.get("headimgUrl")
            item_data["author_id"] = str(result.get("authorUid")) if result.get("authorUid") else None

            answer_list = result.get("answerList")
            if answer_list:
                answer_sum = ""
                for answer in answer_list:
                    answer_content = answer.get("content")
                    if answer_content:
                        answer_sum = answer_sum + answer_content + "<||>"
                    item_data["comment"] = answer_sum

            if item_data["item_id"]:
                # MyTuDao.upsert(**item_data)

                print(item_data)
                PgTuDao.upsert(**item_data)





if __name__ == '__main__':

    # for i in range(1000):
    #
    #     moenApp.send_task("moen.tu8tu.list", args=(i,))

    test_data = [{
        "title": "title",
        "nickname": "nickname",
        "item_id": "35673",
        "share_url": "www.baidu.com"
    }]

    b_data = {'brand': 'word', 'title': '天恒摩墅-156平米-日式风格装修案例18616926', 'nickname': '东易日盛装饰', 'item_type': 'beautyChart', 'item_id': '20908707', 'share_url': 'https://m.to8to.com/xiaoguotu/p20908707.html', 'create_time': '2021-03-31 15:24:04', 'collect_num': 0, 'praise_num': 0, 'comment_num': 0, 'pic_url': 'https://pic.t8tcdn.com/case/case/2103/31/20210331_f2afb6accdcb3ca639c45gb9y4pg4rie.jpg?x-oss-process=image/auto-orient,1/format,webp/watermark,t_100,color_FFFFFF,size_20,shadow_50,g_se,x_20,y_20,text_5Zyf5be05YWUQOS4nOaYk-aXpeebm-ijhemlsA', 'content': '', 'author_avatar': 'https://pic.to8to.com/user/63/headphoto_16371163.jpg?1621994400', 'author_id': '16371163'}
    # PgTuDao.upsert(**b_data)




    # for i in range(5, 20):
    #     print(f"page:{i}")
    #     tu8tu(i, "摩恩")
    #     time.sleep(random.uniform(0, 1))

    # tu8tu_user()
    tu8tu(1, "摩恩")
    # tu8tu_question(test_data)
    # tu8tu_article(test_data)

    # tu8tu_picture(test_data)

    # tu8tu_diary(test_data)

    # print('今天贴次卧的地砖😊😊')

    # tu8tu(19)

    # tu8tu_xiang()
    # import urllib
    # text = "args=%7B%22pubArgs%22%3A%22%7B%5C%22channel%5C%22%3A%5C%22%E5%B0%8F%E7%B1%B3%5C%22%2C%5C%22appversion%5C%22%3A%5C%228.17.3%5C%22%2C%5C%22systemversion%5C%22%3A%5C%2225%5C%22%2C%5C%22apkPackageName%5C%22%3A%5C%22com.to8to.housekeeper%5C%22%2C%5C%22appid%5C%22%3A%5C%2215%5C%22%2C%5C%22version%5C%22%3A%5C%222.5%5C%22%2C%5C%22appostype%5C%22%3A%5C%221%5C%22%2C%5C%22appversioncode%5C%22%3A%5C%2291730%5C%22%2C%5C%22cityName%5C%22%3A%5C%22%E4%B8%8A%E6%B5%B7%5C%22%2C%5C%22deviceModel%5C%22%3A%5C%22sailfish-Pixel%5C%22%2C%5C%22device%5C%22%3A%5C%22google-Pixel%5C%22%2C%5C%22first_id%5C%22%3A%5C%22633540b26c1363ba493fb03c9b0641a1%5C%22%2C%5C%22isnew%5C%22%3A%5C%221%5C%22%2C%5C%22imei%5C%22%3A%5C%22633540b26c1363ba493fb03c9b0641a1%5C%22%2C%5C%22cityId%5C%22%3A%5C%221103%5C%22%2C%5C%22cityid%5C%22%3A%5C%221103%5C%22%2C%5C%22t8t_device_id%5C%22%3A%5C%22633540b26c1363ba493fb03c9b0641a1%5C%22%2C%5C%22uid%5C%22%3A%5C%2216864430%5C%22%2C%5C%22ticket%5C%22%3A%5C%22HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar%5C%22%2C%5C%22to8to_token%5C%22%3A%5C%22HuOZZ1GxtxxSlPJOliULlnKd8bWD3n37A_pRAtJPxLG2_2yqGX4aoEydOT8Nai_G8lHstaeUwjFPwXxrBgzXWSktaErR8Zp9ErtaOEVYqhdyyedAVivc_LFWAXgO1Uar%5C%22%2C%5C%22accountId%5C%22%3A%5C%2224365073%5C%22%7D%22%2C%22oldaid%22%3A14784214%2C%22slideCount%22%3A1%7D"
    # print(urllib.urldecode(text))
