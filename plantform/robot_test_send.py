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

# target_topic = 'req_bid_to_spider'
target_topic = 'req_bid_to_spider_test'

bootstrap_servers = ['172.16.63.83:9092', '172.16.113.148:9092', '172.16.135.145:9092']

class Translate:
    def __init__(self):

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

    def send(self, params, data_type):

        sf = SonyFlake()
        next_id = sf.next_id()
        final_data = {
            "version": 1,
            # "trace_sn": str(next_id),
            "trace_sn": '448969374666116059',
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + time.strftime('%z',
                                                                                                       time.localtime()),
            "data_type": data_type,
            "data": params
        }

        print(final_data)
        self.producer.send(target_topic, final_data,).add_callback(self.on_send_success).add_errback(self.on_send_error)
        self.producer.flush()


    def on_send_success(self, record_metadata):
        print("发送到：topic:{} partition:{} offset:{}".format(record_metadata.topic, record_metadata.partition,
                                                       record_metadata.offset))

    def on_send_error(self, excp):
        print(excp)






# consume earliest available messages, don't commit offsets
# KafkaConsumer(auto_offset_reset='earliest', enable_auto_commit=False)

# consume json messages
# KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('ascii')))


if __name__ == '__main__':

    tran = Translate()
    # # tran.check()
    # tran.run()
    # data_type = "company_search"  # A

    # data_type = "company_win_product"    # B
    # data_type = "company_competitor_analysis"    # C

    # data_type = "company_bidding_info"  # D

    # data_type = "company_bidding_data"  # F

    # data_type = "company_cooperative_buyers"  # E

    # data_type = "company_product_data_report"  # G

    data_type = "req_bid_to_spider"

    # data_type = 'wechat_sougou'

    # params = {
    #     "job_id": "1330100716105851",
    #     # "companies": ["优刻得科技股份有限公司", '北京金隅琉水环保科技有限公司']
    #     # "companies": ["大数据"]
    #     "companies": ['霍尔果斯市农业农村局', '北京金隅琉水环保科技有限公司']
    #     # "keywords": ['广州亮风台信息科技有限公司']
    # }

    # params = {
    #     "job_id": "1330100716105851",
    #     "companies": [{
    #         "name": "内蒙古蒙牛乳业（集团）股份有限公司",
    #         # "products": ["人工智能", "交换机"]
    #     }]
    # }

    # params = {
    #         "job_id": "baa2dd431a6737dfcc5964aecbf8fd53-suggest_concern-0",
    #         "keywords": ["北京辰安科技股份有限公司",
    #                      "立业贷",
    #                      "小鹰信息",
    #                      "领投羊",
    #                      "模信网",
    #                      "星光印刷",
    #                      "达州发展",
    #                      "广州市中智软件开发",
    #                      "whoolala呼啦啦",
    #                      "怡置星怡",
    #                      "人人视频",
    #                      "云行",
    #                      "美遇",
    #                      "中弘集团",
    #                      "深圳联交所",
    #                      "中恒宠物",
    #                      "上海桑祥",
    #                      "朱印船",
    #                      "yogu",
    #                      "三维科技",
    #                      "伊远科技",
    #                      "星曜半导体",
    #
    #                      ]
    #     }

    # params = {
    #     "job_id": "1330100716105851",
    #     "companies": [{
    #             "name": "某部",
    #             "products": ["大数据与AI研发类"]
    #     }]
    #
    # }

    # p = {
    #     "version": 1,
    #     "data": {
    #         "job_id": "baa2dd431a6737dfcc5964aecbf8fd53-suggest_concern-0",
    #         "keywords": ["北京辰安科技股份有限公司"]
    #     },
    #     "data_type": "company_search",
    #     "timestamp": "2023-03-16T14:03:59.494+0800",
    #     "trace_sn": 63671949783547905
    # }


    params = {
        "keywords": ['服务器', '小汽车', '计算机', '数据库']
    }

    tran.send(params, data_type)

    a = [
        {'company_name': '优刻得科技股份有限公司', 'data': [
            {'id': 44372881, 'targetOrgId': 83696, 'targetOrgFullname': '腾讯云计算（北京）有限责任公司', 'tenderCount': 6, 'winCount': 3174, 'customerCount': 1061, 'smNames': ['微服务架构支撑平台二期项目', '视频云服务', '虚拟化及虚拟化管理软件', '公有云租赁项目', '私有云', 'DICT全国集成库', '算力网络低时延']},
            {'id': 10201480, 'targetOrgId': 1426052, 'targetOrgFullname': '深圳华云信息系统有限公司', 'tenderCount': 5, 'winCount': 218, 'customerCount': 52, 'smNames': ['研发服务', '嵌入式研发类', '通用应用系统研发类', '大数据与AI研发类', '研发外协服务框架', '研发服务框架', '通用应用系统']},
            {'id': 32373871, 'targetOrgId': 110641, 'targetOrgFullname': '北京东方国信科技股份有限公司', 'tenderCount': 4, 'winCount': 3013, 'customerCount': 617, 'smNames': ['嵌入式研发类', '研发外协服务框架', '数据治理服务', '云管软件', '数据治理软件', '数据云平台硬件', '领导驾驶舱服务', '对外数据上报服务模块', '数据中心二期项目', '通用应用系统研发类', '大数据与AI研发类']},
            {'id': 32373870, 'targetOrgId': 84655, 'targetOrgFullname': '上海天玑科技股份有限公司', 'tenderCount': 4, 'winCount': 1079, 'customerCount': 341, 'smNames': ['嵌入式研发类', '研发外协服务框架', '通用应用系统研发类', '大数据与AI研发类', '通用应用系统', '云闪付APP内容质量管控']},
            {'id': 10201477, 'targetOrgId': 85771, 'targetOrgFullname': '彩讯科技股份有限公司', 'tenderCount': 5, 'winCount': 979, 'customerCount': 212, 'smNames': ['研发服务', '嵌入式研发类', '通用应用系统研发类', '大数据与AI研发类', '研发外协服务框架', '研发服务框架', '通用应用系统']},
            {'id': 32373865, 'targetOrgId': 89119, 'targetOrgFullname': '杭州东信北邮信息技术有限公司', 'tenderCount': 6, 'winCount': 787, 'customerCount': 155, 'smNames': ['嵌入式研发类', '研发外协服务框架', '专网下数据可控共享平台开发服务', '通用应用系统研发类', '大数据与AI研发类', '研发服务框架', '硬件产品测试技术研究研发服务项目', '通用应用系统']},
            {'id': 373601, 'targetOrgId': 2911, 'targetOrgFullname': '华为技术有限公司', 'tenderCount': 3, 'winCount': 10753, 'customerCount': 2211, 'smNames': ['私有云', '数据中心交换机和管理交换机', '中国移动数据中心和管理交换机', '网络云资源池二期工程数据中心交换机', '中TOR交换机', '中国移动网络云资源池二期数据中心交换机', '中国移动百亿SPN设备', '虚拟化及虚拟化管理软件', 'DICT全国集成库']},
            {'id': 91487839, 'targetOrgId': 30365, 'targetOrgFullname': '浙江大华技术股份有限公司', 'tenderCount': 4, 'winCount': 2310, 'customerCount': 988, 'smNames': ['数字哨兵设备', '门户管理一体机', '办公设备', '手持式数字哨兵设备', '落地式挂壁式数字哨兵设备']},
            {'id': 373603, 'targetOrgId': 503, 'targetOrgFullname': '浪潮软件集团有限公司', 'tenderCount': 8, 'winCount': 6652, 'customerCount': 2080, 'smNames': ['私有云', '数据中心交换机和管理交换机', '中国移动数据中心和管理交换机', '网络云资源池二期工程数据中心交换机', '中TOR交换机', '中国移动网络云资源池二期数据中心交换机', '中国移动百亿SPN设备', '研发服务', '嵌入式研发类', '通用应用系统研发类', '大数据与AI研发类', '研发外协服务框架', '数据运营服务供应商', '研发服务框架', 'DICT全国集成库', '通用应用系统']},
            {'id': 26578550, 'targetOrgId': 45762, 'targetOrgFullname': '上海华讯网络系统有限公司', 'tenderCount': 3, 'winCount': 4410, 'customerCount': 1035, 'smNames': ['服务器', '网络设备', '办公网络建设与优化软硬件']},
            {'id': 8175888, 'targetOrgId': 2431, 'targetOrgFullname': '东软集团股份有限公司', 'tenderCount': 9, 'winCount': 12945, 'customerCount': 3072, 'smNames': ['分布式对象存储', '研发服务', '嵌入式研发类', '通用应用系统研发类', '大数据与AI研发类', '研发外协服务框架', '研发服务框架', '私有云', 'DICT全国集成库', '资源池虚拟化技术支撑框架服务', '通用应用系统', '云闪付APP内容质量管控', 'Ocean智慧服务平台四期工程']},
            {'id': 10199652, 'targetOrgId': 1131343, 'targetOrgFullname': '中商盛达（北京）信息技术有限公司', 'tenderCount': 4, 'winCount': 141, 'customerCount': 69, 'smNames': ['营销短信通道服务', '大数据外部数据短信接口通道项目', '物流类短信资源', '金融类短信资源', '推广类短信资源', '大数据短信通讯类通道']},
            {'id': 1705465, 'targetOrgId': 45852, 'targetOrgFullname': '网宿科技股份有限公司', 'tenderCount': 4, 'winCount': 690, 'customerCount': 252, 'smNames': ['云平台', '云服务', '云安全', '云迁移', '云计算项目-补录', 'CGTN官网数据加速及备份服务', '宽带电视CDN资源加速服务项目', '电stu', '通信网络其他服务', '云基础服务ICT项目', '云基础服务带宽资源']},
            {'id': 32373862, 'targetOrgId': 45223, 'targetOrgFullname': '领航动力信息系统有限公司', 'tenderCount': 3, 'winCount': 1121, 'customerCount': 406, 'smNames': ['嵌入式研发类', '研发外协服务框架', '通用应用系统研发类', '大数据与AI研发类', '通用应用系统']},
            {'id': 7710137, 'targetOrgId': 61952, 'targetOrgFullname': '华为软件技术有限公司', 'tenderCount': 4, 'winCount': 2063, 'customerCount': 439, 'smNames': ['云资源池系统', '亚马逊云全系列服务', '阿里云全系列服务', 'Ucloud云全系列服务', '法律声明公有云产品', '公有云产品合作', '第三方互联网出口带宽租赁', '云基础服务ICT项目', '通信网络其他服务', '云基础服务带宽资源']},
            {'id': 57446651, 'targetOrgId': 46236, 'targetOrgFullname': '中国移动通信集团上海有限公司', 'tenderCount': 4, 'winCount': 1078, 'customerCount': 287, 'smNames': ['数据运营服务供应商', '办公设备', '数字哨兵设备', '手持式数字哨兵设备', '落地式挂壁式数字哨兵设备']}, {'id': 32373863, 'targetOrgId': 47380, 'targetOrgFullname': '亚信科技（中国）有限公司', 'tenderCount': 4, 'winCount': 4327, 'customerCount': 590, 'smNames': ['嵌入式研发类', '研发外协服务框架', '数据运营服务供应商', '无线网络项目软硬件及运维', '创新企业综合服务平台项目']}, {'id': 7710136, 'targetOrgId': 54870, 'targetOrgFullname': '阿里云计算有限公司', 'tenderCount': 3, 'winCount': 4453, 'customerCount': 1236, 'smNames': ['云资源池系统', '亚马逊云全系列服务', '阿里云全系列服务', 'Ucloud云全系列服务', '法律声明公有云产品', '公有云产品合作', '第三方互联网出口带宽租赁', '云基础服务ICT项目', '通信网络其他服务', '云基础服务带宽资源']}, {'id': 10201479, 'targetOrgId': 864958, 'targetOrgFullname': '汉王科技股份有限公司', 'tenderCount': 6, 'winCount': 151, 'customerCount': 72, 'smNames': ['研发服务', '嵌入式研发类', '通用应用系统研发类', '大数据与AI研发类', '研发外协服务框架', '研发服务框架', '硬件产品测试技术研究研发服务项目', '通用应用系统']}, {'id': 48697496, 'targetOrgId': 116807, 'targetOrgFullname': '德勤管理咨询（上海）有限公司', 'tenderCount': 3, 'winCount': 1147, 'customerCount': 440, 'smNames': ['公有云资源服务资格', '数字化转型顶层设计项目']}, {'id': 91487837, 'targetOrgId': 8839, 'targetOrgFullname': '杭州海康威视数字技术股份有限公司', 'tenderCount': 3, 'winCount': 3537, 'customerCount': 1537, 'smNames': ['办公设备', '数字哨兵设备', '手持式数字哨兵设备', '落地式挂壁式数字哨兵设备']}]},
        {'company_name': '霍尔果斯市农业农村局', 'data': [{'data': {}}]}]

    b = {"version": 1, "trace_sn": "448686960836398043", "timestamp": "2023-02-21T16:27:03.184+0800", "data_type": "company_win_product", "data": {"job_id": "1330100716105851", "products": [{"company_name": "\u970d\u5c14\u679c\u65af\u5e02\u519c\u4e1a\u519c\u6751\u5c40", "data": [{"getMoneyTrend": {"x": ["2019", "2020", "2021", "2022", "2023"], "y": [83.37, 3749.31, 16.93, 4395.24, 5723.62]}}, {"getCountTrend": {"x": ["2019", "2020", "2021", "2022", "2023"], "y": [8, 17, 10, 115, 10]}}, {"getOverview": {"ownCount": "160", "money": "1.39\u4ebf", "targetCount": "60"}}]}, {"company_name": "\u4f18\u523b\u5f97\u79d1\u6280\u80a1\u4efd\u6709\u9650\u516c\u53f8", "data": [{"getMoneyTrend": {"x": ["2022"], "y": [0.0]}}, {"getCountTrend": {"x": ["2022"], "y": [1]}}, {"getOverview": {"ownCount": "1", "money": "0.0\u4e07", "targetCount": "1"}}]}]}}
