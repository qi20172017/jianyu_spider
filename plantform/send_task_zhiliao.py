import sys
sys.path.append('/root/other_bid_project/Muto') # 你的项目路径

import hashlib
import json
import datetime
import random
import time

import requests
from app.moen_app import moenApp
from model.rds import rds_206_11



def send_zl_search_keyword():


    key_list = rds_206_11.smembers('zhil_keyword')

    date_list = last_three_days()
    for date in date_list:
        for key in key_list:
            key = key.decode()
            print(key)
            params = {

                'keyword': key,
                'page': 1,
                'date': date
            }

            print(params)
            moenApp.send_task('bid.zhiliao.search', args=(json.dumps(params),), retry=True,
            retry_policy={
                'max_retries': 5,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            },)

def last_three_days():

    # 获取当前日期
    current_date = datetime.date.today()

    # 计算一年前的日期
    one_year_ago = current_date - datetime.timedelta(days=4)

    # 打印出一年前的每一天的日期
    res = []
    while one_year_ago < current_date:
        one_year_ago += datetime.timedelta(days=1)
        res.append(str(one_year_ago))
    return res[:-1]


if __name__ == '__main__':
    import datetime
    send_zl_search_keyword()
    print('发送完成：', str(datetime.date.today()))
    # print(last_three_days())