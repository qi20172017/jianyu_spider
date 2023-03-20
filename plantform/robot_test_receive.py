#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : tranform_bid_data.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/2/15 下午3:09
@Desc  :
nohup python /root/other_bid_project/Muto/plantform/translate_bid_data.py >> /data/bid_project_logs/translate.log 2>&1&

"""

import time
from sonyflake import SonyFlake
from kafka import KafkaConsumer, KafkaProducer
import json
import datetime

source_topic = 'spider_bid_bot_test'
target_topic = 'req_bid_to_spider_test'

bootstrap_servers = ['172.16.63.83:9092', '172.16.113.148:9092', '172.16.135.145:9092']

class Translate:
    def __init__(self):
        self.consumer = KafkaConsumer(source_topic,
                                 group_id='my-group',
                                 # auto_offset_reset='smallest',
                                 value_deserializer=lambda m: json.loads(m.decode('ascii')),
                                 # consumer_timeout_ms=1000,
                                 bootstrap_servers=bootstrap_servers)

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

    def send(self, params, data_type):

        sf = SonyFlake()
        next_id = sf.next_id()
        final_data = {
            "version": 1,
            "trace_sn": str(next_id),
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + time.strftime('%z',
                                                                                                       time.localtime()),
            "data_type": data_type,
            "data": params
        }


        self.producer.send(target_topic, final_data,).add_callback(self.on_send_success).add_errback(self.on_send_error)
        self.producer.flush()


    def on_send_success(self, record_metadata):
        print("发送到：topic:{} partition:{} offset:{}".format(record_metadata.topic, record_metadata.partition,
                                                       record_metadata.offset))

    def on_send_error(self, excp):
        print(excp)


    def run(self):
        print(f'listing at: {source_topic}')
        for message in self.consumer:
            print ("读取到：%s:%d:%d" % (message.topic, message.partition,
                                              message.offset
                                              ))
            print(json.dumps(message.value))
            # if not self.data:
            #     print(f'没有读取到data:{message}')
            #     continue
            # try:
            #     self.check()
            # except Exception as e:
            #     print(f'error:{e},,data:{self.data}')
            data_type = message.value.get('data_type')
            # if data_type == 'company_product_data_report':
            data = message.value.get('data')
            job_id = data.get('job_id')
            products = data.get('products')
            print('job_id: ', job_id, 'data_type: ', data_type)
            # for item in products:
            #     print(item)
            print(products)


if __name__ == '__main__':

    tran = Translate()
    # # tran.check()
    tran.run()

    # data_type = "company_win_product"    # B
    # data_type = "company_competitor_analysis"    # C

    # data_type = "company_bidding_data"  # F

    # data_type = "company_cooperative_buyers"  # E

    # data_type = "company_product_data_report"  # G

