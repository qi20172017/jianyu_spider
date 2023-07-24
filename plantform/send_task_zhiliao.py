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


def send_zl_search_company():



    company_list = [
        '上海八彦图信息科技有限公司',
        '北京医大时代科技发展有限公司',
        '北京昆仑亿发科技股份有限公司',
        '美迪康会议服务有限公司',
        '澳龙信息科技（上海）有限公司',
        '南京弟齐信息技术有限公司',
        '腾讯云计算（北京）有限责任公司',
        '阿里云计算有限公司',
        '京东云计算有限公司',
        '华为云计算技术有限公司',
        '天津市工业和信息化局',
        '宁夏回族自治区商务厅',
    ]

    date =''

    for key in company_list:
        # key = key.decode()
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
    one_year_ago = current_date - datetime.timedelta(days=8)

    # 打印出一年前的每一天的日期
    res = []
    while one_year_ago < current_date:
        one_year_ago += datetime.timedelta(days=1)
        res.append(str(one_year_ago))
    return res[:-3]


if __name__ == '__main__':
    import datetime
    # send_zl_search_keyword()
    send_zl_search_company()
    print('发送完成：', str(datetime.date.today()))
    # print(last_three_days())