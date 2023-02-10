#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : kfk_connect.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/2/6 下午2:44
@Desc  : 
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

class KfkInterface:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=['172.16.63.83:9092', '172.16.113.148:9092', '172.16.135.145:9092'],
                         value_serializer=lambda m: json.dumps(m).encode('ascii')
                         )
    def send_message(self, message):
        future = self.producer.send('spider-bid-info-v1', message)
        result = future.get(timeout=30)
        print(result)

kfk = KfkInterface()

if __name__ == '__main__':
    pass