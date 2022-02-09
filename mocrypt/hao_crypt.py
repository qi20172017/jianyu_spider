import json
import ssl
import requests
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

def genter_list_par(keyword="", page="1", count=100, list_type=""):
    args = {
        "cache_key": "",
        "color": "",
        "from": "history",
        "is_editor_choice": "0",
        "is_owner": "0",
        "keyword": keyword,
        "page": page,
        "pb": {
            "history_count": count
        },
        "recommend_tag": "",
        "search_request_id": "99f27b5df5c2c774ee84c719084b18b3",
        "search_suggest": "0",
        "search_type": "1",
        "tab": "SuggestTab",
        "type": list_type
    }
    url = "http://localhost:8080/calcsig"

    headers = {}

    response = requests.request("POST", url, headers=headers, json=args)

    print(response.text)
    arg1 = response.text
    new_key = arg1.replace('/', '_').replace('+', '-')
    print(new_key)
    B = "qEpcsu2CCkruqxB6h.itrY2p2tx"
    final_key = B + new_key
    print(final_key)
    return final_key


def get_info_par(id_type, obj_id):
    raw_data = {id_type: obj_id}
    arg = {"url": json.dumps(raw_data)}

    url = "http://localhost:8080/calcsig1"
    headers = {}

    response = requests.request("POST", url, headers=headers, json=arg)

    print(response.text)
    arg1 = response.text
    new_key = arg1.replace('/', '_').replace('+', '-')
    print(new_key)
    B = "qEpcsu2CCkruqxB6h.itrY2p2tx"
    final_key = B + new_key
    print(final_key)
    return final_key


def get_info_par_zhengwu(obj_id):
    arg2 = {
        "article_id": obj_id,
        "is_preview": "0",
        "my_home": "0",
        "sugg_tag": ""
    }
    url = "http://localhost:8080/calcsig2"
    # url = "http://172.16.7.115:8080/calcsig2"
    headers = {}
    response = requests.request("POST", url, headers=headers, json=arg2)
    print(response.text)
    arg1 = response.text
    arg1_raw = "7JqA6UUpyVX+wYpc4oS+ArSS245vnTaUWn3Cfjw1MJJ7IfIv4ONTY2q8K71OuWFA8ajk9hzC/5waFhi+H0QGxUXB7PBIRnO6mUGPOLlkqZZGWSVv"
    print("raw::", arg1_raw)
    new_key = arg1.replace('/', '_').replace('+', '-')
    print(new_key)
    B = "qEpcsu2CCkruqxB6h.itrY2p2tx"
    final_key = B + new_key
    print(final_key)
    return final_key

def test_crawl(arg1):

    url = "https://yapi.haohaozhu.cn/multicontentsearch/GetList"
    final_key = gen_replace(arg1)

    payload = f"shawshank=qEpcsu2CCkruqxB6h.itrY2p2tx{final_key}&basic_info=%7B%22%24app_version%22%3A%224.25.0%22%2C%22%24carrier%22%3A%22%E8%81%94%E9%80%9A%22%2C%22%24lib%22%3A%22Android%22%2C%22%24lib_version%22%3A%221.6.19%22%2C%22%24manufacturer%22%3A%22Google%22%2C%22%24os%22%3A%22Android%22%2C%22%24os_version%22%3A%227.1.2%22%2C%22%24screen_height%22%3A1794%2C%22%24screen_width%22%3A1080%2C%22distinct_id%22%3A%22633540b26c1363ba493fb03c9b0641a1%22%2C%22isProxy%22%3A1%7D"
    headers = {
        'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; Pixel Build/N2G47O)hhz4.25.0-did633540b26c1363ba493fb03c9b0641a1-h1d6b06457973df2d2927a14-uid12233866-vid_455c665e676a2f0b9a15171a4916979d-proxy-k3vo9-emu0',
        'cookie': 'visitor_token=vid_455c665e676a2f0b9a15171a4916979d; hhz_token=82fd9bb4134251a3ce424493e8163bdd',
        'content-type': 'application/x-www-form-urlencoded',
        'content-length': '818',
        'accept-encoding': 'gzip',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    print(response.text)


def gen_replace(arg1):
    new_key = arg1.replace('/', '_').replace('+', '-')
    B = "qEpcsu2CCkruqxB6h.itrY2p2tx"
    final_key = B + new_key
    print(final_key)
    return final_key


if __name__ == '__main__':
    arg1 = "b2kXnG85tW3oBOijP1tLR9RNTPg6jcuI3P9Z2SpwSlm7i/PfXnSaXIkujHpmbE+aPaeXYwo72Yih/oTwqex7SScVPmscyz4RxvTvNtQXCPgkiHoy0BWl63C+tU3nKcGtWAFthB/FkT1p3Gi69YL1B4bcvaQ2leGOKB5SDoXUXu+mJ7/FxK5ElSSRMG3FhQoFgjij/z6zmyms3g1ASnq1mMsP9wiBi4Heh4RIUSWBYjKIWxBn0O0CgwSYTlB9sPlKSzHAwPkYeuqe1DYDcEpAL86l+nIrd8PLFephEuCa4AIRsllrUnO7KGxzEEtOXiB3C9LyBbao9gJeZJwpgLBPCtFws3eCbkoBs67RYw=="
    test_crawl(arg1)
