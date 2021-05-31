import ssl
from mocrypt.hao_crypt import *
from common.tools import safe_get, time_exchange
from model.pg.pg_dao.pg_hao_dao import PgHaoDao
from app.moen_app import moenApp
from plantform.weapon import *
from common.tools import random_sleep
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

TYPE_IDCT = {
    0: "图片，问答",
    1: "整屋",  #
    5: "文章",
}


@moenApp.task(
    name='moen.haozu.list',
    bind=True,
    acks_late=True,
    rate_limit='10/m',
    # autoretry_for=(HttpError, TypeError, WeiXinError, TError),
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def haozu(self, page, key_word, list_type=""):
    random_sleep(1,5)

    url = "https://yapi.haohaozhu.cn/multicontentsearch/GetList"
    par = genter_list_par(key_word, page, list_type=list_type)
    payload = f"shawshank={par}&basic_info=%7B%22%24app_version%22%3A%224.25.0%22%2C%22%24lib%22%3A%22Android%22%2C%22%24lib_version%22%3A%221.6.19%22%2C%22%24manufacturer%22%3A%22Google%22%2C%22%24os%22%3A%22Android%22%2C%22%24os_version%22%3A%227.1.2%22%2C%22%24screen_height%22%3A1794%2C%22%24screen_width%22%3A1080%2C%22distinct_id%22%3A%22633540b26c1363ba493fb03c9b0641a1%22%2C%22isProxy%22%3A1%7D"

    headers = {
        'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; Pixel Build/N2G47O)hhz4.25.0-did633540b26c1363ba493fb03c9b0641a1-h16717b566b760db97937515-uid12233866-vid_455c665e676a2f0b9a15171a4916979d-proxy-k3vo9-emu0',
        'cookie': 'visitor_token=vid_455c665e676a2f0b9a15171a4916979d; hhz_token=82fd9bb4134251a3ce424493e8163bdd',
        'content-type': 'application/x-www-form-urlencoded',
        'content-length': '772',
        'accept-encoding': 'gzip',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    print(response.text)
    raw_data = response.text
    if raw_data:
        raw_data = json.loads(raw_data)
        rows = safe_get(raw_data, "data", "rows")
        if rows:
            for row in rows:
                result_data = {}

                result_data["item_type"] = safe_get(row, "type")
                result_data["brand"] = key_word

                if result_data["item_type"] == 0:
                    hao_photo(result_data, row)
                elif result_data["item_type"] == 1:
                    hao_house(result_data, row)

                elif result_data["item_type"] == 5:
                    hao_article(result_data, row)
            next_page = page + 1
            save_page("haozu",key_word, next_page)
            moenApp.send_task("moen.haozu.list", args=(next_page, key_word))
        else:
            print("没有更多了")



def hao_photo(result_data, row):
    video_info = safe_get(row, "photo", "photo_info", "video_info")
    if video_info:
        result_data["item_type"] = "视频"
        result_data["video_url"] = safe_get(video_info, "play_url")
        result_data["pic_url"] = safe_get(video_info, "pic_url")
    image_list = safe_get(row, "photo", "photo_info", "image_list")
    if image_list:
        result_data["item_type"] = "图片||问答"
        pic_url = ''
        for image in image_list:
            pic_url = pic_url + safe_get(image, "pic_url") + "<||>"
        result_data["pic_url"] = pic_url

    result_data["author_id"] = safe_get(row, "photo", "user_info", "uid")
    result_data["author_avatar"] = safe_get(row, "photo", "user_info", "avatar")
    result_data['nickname'] = safe_get(row, "photo", "user_info", "nick")
    str_data = safe_get(row, "photo", "photo_info", "remark")
    if str_data:
        result_data['title'] = str_data.strip()[:20]
        result_data['content'] = str_data.strip()
    result_data['item_id'] = safe_get(row, "photo", "photo_info", "id")
    result_data['create_time'] = safe_get(row, "photo", "photo_info", "addtime")
    if result_data["create_time"] and result_data["create_time"] != 0 and result_data["create_time"] != "0":
        result_data["create_time"] = time_exchange(int(result_data["create_time"]))
    else:
        result_data["create_time"] = None

    result_data["collect_num"] = safe_get(row, "photo", "counter", "favorite")
    result_data["praise_num"] = safe_get(row, "photo", "counter", "like")
    result_data["comment_num"] = safe_get(row, "photo", "counter", "comments")

    result_data["topic"] = safe_get(row, "photo", "photo_info", "topic", "title")
    result_data["share_url"] = safe_get(row, "photo", "photo_info", "share_url")

    if result_data["item_id"]:
        print(result_data)
        PgHaoDao.upsert(**result_data)
    print(50 * '-')


def hao_article(result_data, row):
    result_data["item_type"] = "文章"

    result_data["author_id"] = safe_get(row, "blank", "user_info", "uid")
    result_data["author_avatar"] = safe_get(row, "blank", "user_info", "avatar")
    result_data['nickname'] = safe_get(row, "blank", "user_info", "nick")

    result_data['item_id'] = safe_get(row, "blank", "blank_info", "bid")
    result_data['title'] = safe_get(row, "blank", "blank_info", "title")
    result_data['content'] = safe_get(row, "blank", "blank_info", "remark")
    result_data["cover_url"] = safe_get(row, "blank", "blank_info", "cover_pic_url")
    result_data['create_time'] = safe_get(row, "blank", "blank_info", "publish_time")
    if result_data["create_time"] and result_data["create_time"] != 0 and result_data["create_time"] != "0":
        result_data["create_time"] = time_exchange(int(result_data["create_time"]))
    else:
        result_data["create_time"] = None

    result_data["collect_num"] = safe_get(row, "blank", "counter", "favorite")
    result_data["praise_num"] = safe_get(row, "blank", "counter", "like")
    result_data["comment_num"] = safe_get(row, "blank", "counter", "comments")

    result_data["share_url"] = safe_get(row, "blank", "photo_info", "share_url")

    if result_data["item_id"]:
        print(result_data)
        PgHaoDao.upsert(**result_data)
        moenApp.send_task("moen.haozu.article", args=(result_data["item_id"],))

    print(50 * '-')
    # info_article(result_data['item_id'])


def hao_house(result_data, row):
    result_data["item_type"] = "整屋"

    result_data["author_id"] = safe_get(row, "article", "user_info", "uid")
    result_data["author_avatar"] = safe_get(row, "article", "user_info", "avatar")
    result_data['nickname'] = safe_get(row, "article", "user_info", "nick")

    result_data['item_id'] = safe_get(row, "article", "article_info", "aid")
    result_data['title'] = safe_get(row, "article", "article_info", "title")
    result_data['content'] = safe_get(row, "article", "article_info", "remark")
    result_data["pic_url"] = safe_get(row, "article", "article_info", "cover_pic_url")
    result_data['create_time'] = safe_get(row, "article", "article_info", "publish_time")
    if result_data["create_time"] and result_data["create_time"] != 0 and result_data["create_time"] != "0":
        result_data["create_time"] = time_exchange(int(result_data["create_time"]))
    else:
        result_data["create_time"] = None
    result_data['area'] = safe_get(row, "article", "article_info", "house_size")

    result_data["collect_num"] = safe_get(row, "article", "counter", "favorite")
    result_data["praise_num"] = safe_get(row, "article", "counter", "like")
    result_data["comment_num"] = safe_get(row, "article", "counter", "comments")

    if result_data["item_id"]:
        print(result_data)
        PgHaoDao.upsert(**result_data)
        moenApp.send_task("moen.haozu.house", args=(result_data["item_id"],))

    print(50 * '-')
    # info_house(result_data['item_id'])


@moenApp.task(
    name='moen.haozu.house',
    bind=True,
    acks_late=True,
    rate_limit='10/m',
    # autoretry_for=(HttpError, TypeError, WeiXinError, TError),
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def info_house(self, obj_id):
    random_sleep(1,5)

    par = get_info_par_zhengwu(obj_id)

    url = "https://yapi.haohaozhu.cn/Article/detail"

    payload = f"shawshank={par}&basic_info=%7B%22%24app_version%22%3A%224.25.0%22%2C%22%24lib%22%3A%22Android%22%2C%22%24lib_version%22%3A%221.6.19%22%2C%22%24manufacturer%22%3A%22Google%22%2C%22%24os%22%3A%22Android%22%2C%22%24os_version%22%3A%227.1.2%22%2C%22%24screen_height%22%3A1794%2C%22%24screen_width%22%3A1080%2C%22distinct_id%22%3A%22633540b26c1363ba493fb03c9b0641a1%22%2C%22isProxy%22%3A1%7D"
    headers = {
        'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; Pixel Build/N2G47O)hhz4.25.0-did633540b26c1363ba493fb03c9b0641a1-h12bddb01d3cd1bea9987318-uid12233866-vid_455c665e676a2f0b9a15171a4916979d-proxy-k3vo9-emu0',
        'cookie': 'visitor_token=vid_455c665e676a2f0b9a15171a4916979d; hhz_token=82fd9bb4134251a3ce424493e8163bdd',
        'content-type': 'application/x-www-form-urlencoded',
        'content-length': '520',
        'accept-encoding': 'gzip',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    print(response.text)
    print("整屋详情")
    raw_data = response.text
    if raw_data:
        raw_data = json.loads(raw_data)
        house_data = safe_get(raw_data, "data")
        if house_data:
            result_data = {}

            result_data['item_id'] = safe_get(house_data, "article_id")
            result_data['city_name'] = safe_get(house_data, "article_info", "house_info", "area_ch")
            result_data['area'] = safe_get(house_data, "article_info", "house_info", "house_size")
            result_data['product_sum'] = safe_get(house_data, "article_info", "house_info", "house_stuff")
            result_data['house_type'] = safe_get(house_data, "article_info", "house_info", "room")

            question_list = safe_get(house_data, "article_info", "question_info", "question_list")
            if question_list:
                comment = ""
                for question in question_list:
                    comment = comment + question.get("text") + "||" + question.get("title") + "<<>>"
                result_data["comment"] = comment

            if result_data["item_id"]:
                print(result_data)
                PgHaoDao.upsert(**result_data)
            print(50 * '-')


@moenApp.task(
    name='moen.haozu.article',
    bind=True,
    acks_late=True,
    rate_limit='6/m',
    # autoretry_for=(HttpError, TypeError, WeiXinError, TError),
    retry_kwargs={
        "max_retries": 20,
        "default_retry_delay": 1
    }
)
def info_article(self, obj_id):
    random_sleep(1,5)

    url = "https://yapi.haohaozhu.cn/Blank/detail"
    par = get_info_par("blank_id", obj_id)
    payload = f"shawshank={par}&basic_info=%7B%22%24app_version%22%3A%224.25.0%22%2C%22%24lib%22%3A%22Android%22%2C%22%24lib_version%22%3A%221.6.19%22%2C%22%24manufacturer%22%3A%22Google%22%2C%22%24os%22%3A%22Android%22%2C%22%24os_version%22%3A%227.1.2%22%2C%22%24screen_height%22%3A1794%2C%22%24screen_width%22%3A1080%2C%22distinct_id%22%3A%22633540b26c1363ba493fb03c9b0641a1%22%2C%22isProxy%22%3A1%7D"
    headers = {
        'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; Pixel Build/N2G47O)hhz4.25.0-did633540b26c1363ba493fb03c9b0641a1-h1db15e0d6bddab5a9997f1c-uid12233866-vid_455c665e676a2f0b9a15171a4916979d-proxy-k3vo9-emu0',
        'cookie': 'visitor_token=vid_455c665e676a2f0b9a15171a4916979d; hhz_token=82fd9bb4134251a3ce424493e8163bdd',
        'content-type': 'application/x-www-form-urlencoded',
        'content-length': '456',
        'accept-encoding': 'gzip',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print(response.text)
    raw_data = response.text
    if raw_data:
        result_data = {}
        raw_data = json.loads(raw_data)
        article_info = safe_get(raw_data, "data")

        result_data['item_id'] = safe_get(article_info, "blank_info", "bid")

        content_list = safe_get(article_info, "blank_info", "content_list")
        if content_list:
            content = ''
            pic_url = ''
            for sub_content in content_list:
                text = safe_get(sub_content, "content", "text")
                if text:
                    content += text
                url = safe_get(sub_content, "pic", "url")
                if url:
                    pic_url = pic_url + url + "<||>"

            result_data['long_content'] = content
            result_data["pic_url"] = pic_url

        if result_data["item_id"]:
            print(result_data)
            PgHaoDao.upsert(**result_data)
        print(50 * '-')


if __name__ == '__main__':
    obj_id_zhengwu = "0002bn601002sxak"
    blank_id = "0002noq050001426"
    note_id = "001qytd00003muyh"
    note_id2 = "001p9030000462pr"

    # info_photo(note_id2)
    # info_house(obj_id_zhengwu)
    # info_article(blank_id)

    # raw_data = {"bland_id": "0001r4605000o20n"}
    # genter_list_par()
    # genter_par()

    # moenApp.send_task("moen.haozu.article", args=(blank_id,))
    # moenApp.send_task("moen.haozu.house", args=(obj_id_zhengwu,))

    key_word = "摩恩"
    page = 30
    list_type = ""
    haozu(key_word=key_word, page=page, list_type=list_type)

    # ja_test()
    # genter_par()
    # hao_list()
    # user_info()
    # str1 = "    1qweerrsfd"
    # print(str1.strip())
    # print(str1[:20])
