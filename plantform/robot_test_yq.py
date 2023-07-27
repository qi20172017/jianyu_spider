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
import datetime

source_topic = 'user_subject_3357724503697408'
# source_topic = 'useful_test'

bootstrap_servers = ["xgsj-kafka.istarshine.com:9092", "xgsj-kafka.istarshine.com:9093",
                     "xgsj-kafka.istarshine.com:9094"]

security_protocol = 'SASL_PLAINTEXT'
sasl_mechanism = 'PLAIN'
sasl_plain_username = 'u782135'
sasl_plain_password = 'e250e863f6a511e8b4c79cb6d002907c'


class Translate:
    def __init__(self):
        self.consumer = KafkaConsumer(source_topic,
                                      group_id="group_ysf",
                                      # auto_offset_reset='smallest',
                                      auto_offset_reset='latest',
                                      # value_deserializer=lambda m: json.loads(m.decode('ascii')),
                                      value_deserializer=lambda m: json.loads(m.decode('utf8')),
                                      # consumer_timeout_ms=1000,
                                      bootstrap_servers=bootstrap_servers,

                                      security_protocol=security_protocol,
                                      sasl_mechanism=sasl_mechanism,
                                      sasl_plain_username=sasl_plain_username,
                                      sasl_plain_password=sasl_plain_password
                                      )

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

    def on_send_success(self, record_metadata):
        print("发送到：topic:{} partition:{} offset:{}".format(record_metadata.topic, record_metadata.partition,
                                                           record_metadata.offset))

    def on_send_error(self, excp):
        print(excp)

    def run(self):
        print(f'listing at: {source_topic}')
        count = 0
        for message in self.consumer:
            print("读取到：%s:%d:%d" % (message.topic, message.partition,
                                    message.offset
                                    ))
            # print(message.value)
            print(count)
            count += 1
            # print(json.dumps(message.value))
            # data_type = message.value.get('data_type')
            # data = message.value.get('data')
            # user_logic = message.value.get('user_logic')
            # # words = user_logic['result'][0]['words']
            #
            # title = data.get('title')
            # url = data.get('url')
            # ctime = data.get('ctime')
            #
            #
            # # timestamp = 1690182360
            # dt_object = datetime.datetime.fromtimestamp(int(ctime))
            #
            # # print("日期时间对象:", dt_object)
            # ctime = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            #
            # content = data.get('content')
            # print(ctime,  'url: ', url, 'title: ', title, 'content: ', content)

            # print(products)

[
    {"quantity": 850, "formattedQuantity": "850", "price": "0.177", "formattedPrice": "$0.177"},
    {"quantity": 1700, "formattedQuantity": "1,700", "price": "0.162", "formattedPrice": "$0.162"},
    {"quantity": 2550, "formattedQuantity": "2,550", "price": "0.159", "formattedPrice": "$0.159"},
    {"quantity": 4250, "formattedQuantity": "4,250", "price": "0.152", "formattedPrice": "$0.152"},
    {"quantity": 5950, "formattedQuantity": "5,950", "price": "0.149", "formattedPrice": "$0.149"},
    {"quantity": 9350, "formattedQuantity": "9,350", "price": "0.147", "formattedPrice": "$0.147"}
]


if __name__ == '__main__':
    tran = Translate()

    tran.run()

    # # tran.check()
    a = {'user_logic':
        {'result': [
            {
                'username': '上海优司服信息科技有限公司',
                'subject_type': '0',
                'user_id': 3357724503697408,
                'parent_subject_id': '',
                'subject_id': '3387506233428992',
                'team_id': '',
                'word_pos': [['阿里巴巴', 573, 585, 2]],
                'words': ['阿里巴巴'],
                'logic': '',
                'parent_user_id': '',
                'subject_attr': '1',
                'subject': 'test_or1'
            }
        ]
        },
        'index_suffix': 'news',
        'user_words': {
            'excepted': [],
            'ctime': 1690185272
        },
        '__router_time': 1690185271.271235,
        '__router_id': '192.168.191.63_router4-thor-7c99d548f6-kcnz7_thor',
        '__ctime': None,
        'flt6_in_ts': 1690185272.122829,
        'filter_id': 'filter-service-rmqthrift-569c6f76bf-jcbcw',
        '__gtime': None,
        'flt6_id': '192.168.224.133|flt6-dowding-rmqthrift-74c48bd8fc-sl5pl|filter_service6:V6.0.837',
        'data': {
            'publisher': {
                'platform': '独立网站',
                'entity': '',
                'site_name': '',
                'id': 'sohu.com|',
                'name': ''
            },
            'uuid': '522bfa4e29f711ee9f7fc6af74912734',
            'title': '阿里旗下电商公司增资至2000万 阿里溢六发发电商公司更名淘天电商',
            'url': 'https://www.sohu.com/a/705728845_114984',
            'content_xml': '<article class="article" id="mp-editor">\n    <!-- 政务处理 -->\n          <p data-role="original-title" style="display:none">原标题：阿里旗下电商公司增资至2000万 阿里溢六发发电商公司更名淘天电商</p>\n              <!--          -->\n            <p>天眼查App显示，近日，杭州溢六发发电子商务有限公司发生工商变更，企业名称变更为杭州淘天电子商务科技有限公司，同时注册资本由50万人民币增至2000万人民币，增幅3900%。</p> \n<p>该公司成立于2021年11月，法定代表人为刘蓓，经营范围含互联网销售、电子产品销售、软件开发、数字文化创意内容应用服务、个人互联网直播服务等，由阿里巴巴（中国）网络技术有限公司全资持股。</p> \n<p>来源：金融界天眼查<a href="//www.sohu.com/?strategyid=00001%20" target="_blank" title="点击进入搜狐首页" id="backsohucom" style="white-space: nowrap;"><span class="backword"><i class="backsohu"></i>返回搜狐，查看更多</span></a></p>          <!-- 政务账号添加来源标示处理 -->\n      <!-- 政务账号添加来源标示处理 -->\n      <p data-role="editor-name">责任编辑：<span></span></p>\n</article>\n',
            'gather':
                {'site_name': '搜狐新闻',
                 'sub_domain': ['www.sohu.com'],
                 'site_domain': 'sohu.com',
                 'info_flag': ['01', '0101'],
                 'gtime': 1690185269},
            'mid': '705728845_114984',
            'analysis': {
                'noise': 0,
                'sentiment': 0,
                'summary': '    \n          \n              \n            天眼查App显示，近日，杭州溢六发发电子商务有限公司发生工商变更，企业名称变更为杭州淘天电子商务科技有限公司，同时注册资本由50万人民币增至2000万人民币，增幅3900%。 ',
                'info_src': {
                    'loc': {'province': '北京市', 'city': '北京市', 'name': ['北京市', '北京市', None], 'level': 2},
                    'domain': 'sohu.com', 'name': '搜狐', 'lv': {'name': 'B', 'level': '5'}, 'type': 1,
                    'cls': {'name': ['综合门户'], 'level': 1}}, 'hashtag': [],
                'find_address': {'province': ['浙江省'], 'city': ['杭州市'], 'district': [],
                                 'province_count': 1, 'words': ['杭州'], 'district_count': 0,
                                 'city_count': 1}, 'mentions': [],
                'hashcode': {'1': 4482167140185984767, '3': 2283992869522062830,
                             '2': 1006993725211691027, '5': 8049359931589916325},
                'classify': {'result': [], 'ctime': 1690185272.123411}},
            'content': '\n    \n          \n              \n            天眼查App显示，近日，杭州溢六发发电子商务有限公司发生工商变更，企业名称变更为杭州淘天电子商务科技有限公司，同时注册资本由50万人民币增至2000万人民币，增幅3900%。 \n该公司成立于2021年11月，法定代表人为刘蓓，经营范围含互联网销售、电子产品销售、软件开发、数字文化创意内容应用服务、个人互联网直播服务等，由阿里巴巴（中国）网络技术有限公司全资持股。 \n来源：金融界天眼查返回搜狐，查看更多          \n      \n      责任编辑：\n\n',
            'reply_count': 0, 'user': {'profile_img_url': '', 'name': '金融界',
                                       'url': 'https://mp.sohu.com/profile?xpt=MTcwNDEwMzE4M0BzaW5hLnNvaHUuY29t',
                                       'ip_region': ['北京市'], 'nickname': '金融界', 'uid': '114984'},
            'visit_count': 0,
            'wtype': 1,
            'channel': '搜狐新闻',
            'ctime': 1690182360
        }
    }
