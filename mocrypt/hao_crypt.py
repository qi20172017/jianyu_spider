import json
import requests

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
    # url = "http://172.16.7.115:8080/calcsig"

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
    # url = "http://172.16.7.115:8080/calcsig1"
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