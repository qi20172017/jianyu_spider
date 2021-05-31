import time
from model.rds import rds_100_2
from app.moen_app import moenApp


def save_time(key_word, new_time):
    raw_data = rds_100_2.hget("moen_time", key_word)
    if raw_data:
        flag_time = int(raw_data.decode())
    else:
        rds_100_2.hset("moen_time", key_word, new_time)
        return
    rds_100_2.hset("moen_time", key_word, min(int(new_time), flag_time))


def save_page(plantform, key_word, page):
    rds_100_2.hset("moen_page", plantform + '_'+ key_word, page)


def send_next_page(total, page, key_word):
    if total and total > 0 and reduced_time(key_word):
        next_page = page + 1
        moenApp.send_task("moen.tu8tu.list", args=(next_page, key_word))
        print(f"发送成功：{next_page} 页")
    else:
        print(f"当前页：{page},没有更多了")


def reduced_time(key_word):
    """
    在范围内，返回True
    :param key_word:
    :return:
    """
    target = 1588262400  # 2020-05-01 00:00:00
    raw_data = rds_100_2.hget("moen_time", key_word)
    if not raw_data:
        flag_time = 1622025566
        save_time(key_word, flag_time)  # 2021-05-26 18:39:26
    else:
        flag_time = int(raw_data.decode())
    if flag_time > target:
        return True
    else:
        return False


if __name__ == '__main__':
    # save_data("摩恩", "1619699462")
    # print(reduced_time("摩恩"))
    # print(min(1, 2))
    # print(int(23))
    hun = 'qEpcsu2CCkruqxB6h.itrY2p2tx'

    """
    Gson:obj:: {cache_key=, color=, from=history, is_editor_choice=0, is_owner=0, keyword=%E9%A9%AC%E6%A1%B6, page=1, pb=%7B%22history_count%22%3A61%7D, recommend_tag=, search_request_id=86be465ce870379a4c5bf74021548c02, search_suggest=0, search_type=1, tab=SuggestTab, type=}
    Gson:result:: {"cache_key":"","color":"","from":"history","is_editor_choice":"0","is_owner":"0","keyword":"%E9%A9%AC%E6%A1%B6","page":"1","pb":"%7B%22history_count%22%3A61%7D","recommend_tag":"","search_request_id":"86be465ce870379a4c5bf74021548c02","search_suggest":"0","search_type":"1","tab":"SuggestTab","type":""}

    """

    pass
    key_word = 'IrogSxymhHbgP-cLFAJsR7EsNpGUZsXYbH7aBbs7xvzc5vX0bwDNSN9_ypEc5qWQ_ZhtVPmIClydRLcbvBKmsLZW0ONylPUPo4MxvyRwRbmeCBhDV5eB59mvrnq3CieeVjkXkb4s0JL0yIJpEnMk92k2MBo5NdhxGrQiBaUn9FWyrF0dRHwDhKRQRLwwOkzZmRQkH2QX3QrDYS5nvssO_21J18kEsqyGAfOZH87EKe0U1esUwmyvJQPysiF2nSYMPvRgA7l5NHfVOvHNaJ0KSjCjOy7UKsPFxw2HM1_orXHdBd4P3YkzgjuPAY6tL9RH2P8wDZDj-cirws7r_OxUMmDOwqbTiDZzR8Gd6_srXNJiFeazSYvpxq8TO0BHmhYTf164tYeD6t8QU55b5LWzaN14vGI='
    new_key = key_word.replace('_', '/').replace('-', '+')
    print(key_word)
    print(new_key)
