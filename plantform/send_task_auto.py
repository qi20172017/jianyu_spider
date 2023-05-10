#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : send_task_auto.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/3/31 下午1:34
@Desc  : 
"""
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


def send_jianyu_keyword():

    key_list = rds_206_11.smembers('jianyu:9w_keyword_1') # 这个keyword_1里面是过滤了一遍的

    # key_list = ['1','2','3']
    area_list = [
        "安徽",
        "澳门",
        "北京",
        "重庆",
        "福建",
        "广东",
        "广西",
        "贵州",
        "甘肃",
        "河北",
        "湖北",
        "黑龙江",
        "海南",
        "河南",
        "湖南",
        "吉林",
        "江苏",

        "江西",
        "辽宁",
        "内蒙古",
        "宁夏",
        "青海",
        "山西",
        "陕西",
        "上海",
        "山东",
        "四川",
        "天津",
        "台湾",
        "西藏",
        "新疆",
        "香港",
        "云南",
        "浙江"]

    area_list = ['']

    for area in area_list:
        for keyword in key_list:
            keyword = keyword.decode()
            print(keyword)
            moenApp.send_task('bid.jianyu.search_keyword', args=(json.dumps({
                'keyword': keyword,
                'page': 1,
                'area':area
            }),))
    print(datetime.datetime.now())


def send_zl_search():


    today = datetime.datetime.today()
    yesterday = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    adcodes = [
        {
            "adcode": "320100",
            "city": "南京"
        },
        {
            "adcode": "320200",
            "city": "无锡"
        },
        {
            "adcode": "320300",
            "city": "徐州"
        },
        {
            "adcode": "320400",
            "city": "常州"
        },
        {
            "adcode": "320500",
            "city": "苏州"
        },
        {
            "adcode": "320600",
            "city": "南通"
        },
        {
            "adcode": "320700",
            "city": "连云港"
        },
        {
            "adcode": "320800",
            "city": "淮安"
        },
        {
            "adcode": "320900",
            "city": "盐城"
        },
        {
            "adcode": "321000",
            "city": "扬州"
        },
        {
            "adcode": "321100",
            "city": "镇江"
        },
        {
            "adcode": "321200",
            "city": "泰州"
        },
        {
            "adcode": "321300",
            "city": "宿迁"
        },
        {
            "adcode": "330100",
            "city": "杭州"
        },
        {
            "adcode": "330200",
            "city": "宁波"
        },
        {
            "adcode": "330300",
            "city": "温州"
        },
        {
            "adcode": "330400",
            "city": "嘉兴"
        },
        {
            "adcode": "330500",
            "city": "湖州"
        },
        {
            "adcode": "330600",
            "city": "绍兴"
        },
        {
            "adcode": "330700",
            "city": "金华"
        },
        {
            "adcode": "330800",
            "city": "衢州"
        },
        {
            "adcode": "330900",
            "city": "舟山"
        },
        {
            "adcode": "331000",
            "city": "台州"
        },
        {
            "adcode": "331100",
            "city": "丽水"
        },
        {
            "adcode": "340100",
            "city": "合肥"
        },
        {
            "adcode": "340200",
            "city": "芜湖"
        },
        {
            "adcode": "340300",
            "city": "蚌埠"
        },
        {
            "adcode": "340400",
            "city": "淮南"
        },
        {
            "adcode": "340500",
            "city": "马鞍山"
        },
        {
            "adcode": "340600",
            "city": "淮北"
        },
        {
            "adcode": "340700",
            "city": "铜陵"
        },
        {
            "adcode": "340800",
            "city": "安庆"
        },
        {
            "adcode": "341000",
            "city": "黄山"
        },
        {
            "adcode": "341100",
            "city": "滁州"
        },
        {
            "adcode": "341200",
            "city": "阜阳"
        },
        {
            "adcode": "341300",
            "city": "宿州"
        },
        {
            "adcode": "341500",
            "city": "六安"
        },
        {
            "adcode": "341600",
            "city": "亳州"
        },
        {
            "adcode": "341700",
            "city": "池州"
        },
        {
            "adcode": "341800",
            "city": "宣城"
        },
        {
            "adcode": "350100",
            "city": "福州"
        },
        {
            "adcode": "350200",
            "city": "厦门"
        },
        {
            "adcode": "350300",
            "city": "莆田"
        },
        {
            "adcode": "350400",
            "city": "三明"
        },
        {
            "adcode": "350500",
            "city": "泉州"
        },
        {
            "adcode": "350600",
            "city": "漳州"
        },
        {
            "adcode": "350700",
            "city": "南平"
        },
        {
            "adcode": "350800",
            "city": "龙岩"
        },
        {
            "adcode": "350900",
            "city": "宁德"
        },
        {
            "adcode": "360100",
            "city": "南昌"
        },
        {
            "adcode": "360200",
            "city": "景德镇"
        },
        {
            "adcode": "360300",
            "city": "萍乡"
        },
        {
            "adcode": "360400",
            "city": "九江"
        },
        {
            "adcode": "360500",
            "city": "新余"
        },
        {
            "adcode": "360600",
            "city": "鹰潭"
        },
        {
            "adcode": "360700",
            "city": "赣州"
        },
        {
            "adcode": "360800",
            "city": "吉安"
        },
        {
            "adcode": "360900",
            "city": "宜春"
        },
        {
            "adcode": "361000",
            "city": "抚州"
        },
        {
            "adcode": "361100",
            "city": "上饶"
        },
        {
            "adcode": "370100",
            "city": "济南"
        },
        {
            "adcode": "370200",
            "city": "青岛"
        },
        {
            "adcode": "370300",
            "city": "淄博"
        },
        {
            "adcode": "370400",
            "city": "枣庄"
        },
        {
            "adcode": "370500",
            "city": "东营"
        },
        {
            "adcode": "370600",
            "city": "烟台"
        },
        {
            "adcode": "370700",
            "city": "潍坊"
        },
        {
            "adcode": "370800",
            "city": "济宁"
        },
        {
            "adcode": "370900",
            "city": "泰安"
        },
        {
            "adcode": "371000",
            "city": "威海"
        },
        {
            "adcode": "371100",
            "city": "日照"
        },
        {
            "adcode": "371300",
            "city": "临沂"
        },
        {
            "adcode": "371400",
            "city": "德州"
        },
        {
            "adcode": "371500",
            "city": "聊城"
        },
        {
            "adcode": "371600",
            "city": "滨州"
        },
        {
            "adcode": "371700",
            "city": "菏泽"
        },
        {
            "adcode": "210100",
            "city": "沈阳"
        },
        {
            "adcode": "210200",
            "city": "大连"
        },
        {
            "adcode": "210300",
            "city": "鞍山"
        },
        {
            "adcode": "210400",
            "city": "抚顺"
        },
        {
            "adcode": "210500",
            "city": "本溪"
        },
        {
            "adcode": "210600",
            "city": "丹东"
        },
        {
            "adcode": "210700",
            "city": "锦州"
        },
        {
            "adcode": "210800",
            "city": "营口"
        },
        {
            "adcode": "210900",
            "city": "阜新"
        },
        {
            "adcode": "211000",
            "city": "辽阳"
        },
        {
            "adcode": "211100",
            "city": "盘锦"
        },
        {
            "adcode": "211200",
            "city": "铁岭"
        },
        {
            "adcode": "211300",
            "city": "朝阳"
        },
        {
            "adcode": "211400",
            "city": "葫芦岛"
        },
        {
            "adcode": "220100",
            "city": "长春"
        },
        {
            "adcode": "220200",
            "city": "吉林"
        },
        {
            "adcode": "220300",
            "city": "四平"
        },
        {
            "adcode": "220400",
            "city": "辽源"
        },
        {
            "adcode": "220500",
            "city": "通化"
        },
        {
            "adcode": "220600",
            "city": "白山"
        },
        {
            "adcode": "220700",
            "city": "松原"
        },
        {
            "adcode": "220800",
            "city": "白城"
        },
        {
            "adcode": "222400",
            "city": "延边"
        },
        {
            "adcode": "230100",
            "city": "哈尔滨"
        },
        {
            "adcode": "230200",
            "city": "齐齐哈尔"
        },
        {
            "adcode": "230300",
            "city": "鸡西"
        },
        {
            "adcode": "230400",
            "city": "鹤岗"
        },
        {
            "adcode": "230500",
            "city": "双鸭山"
        },
        {
            "adcode": "230600",
            "city": "大庆"
        },
        {
            "adcode": "230700",
            "city": "伊春"
        },
        {
            "adcode": "230800",
            "city": "佳木斯"
        },
        {
            "adcode": "230900",
            "city": "七台河"
        },
        {
            "adcode": "231000",
            "city": "牡丹江"
        },
        {
            "adcode": "231100",
            "city": "黑河"
        },
        {
            "adcode": "231200",
            "city": "绥化"
        },
        {
            "adcode": "232700",
            "city": "大兴安岭"
        },
        {
            "adcode": "610100",
            "city": "西安"
        },
        {
            "adcode": "610200",
            "city": "铜川"
        },
        {
            "adcode": "610300",
            "city": "宝鸡"
        },
        {
            "adcode": "610400",
            "city": "咸阳"
        },
        {
            "adcode": "610500",
            "city": "渭南"
        },
        {
            "adcode": "610600",
            "city": "延安"
        },
        {
            "adcode": "610700",
            "city": "汉中"
        },
        {
            "adcode": "610800",
            "city": "榆林"
        },
        {
            "adcode": "610900",
            "city": "安康"
        },
        {
            "adcode": "611000",
            "city": "商洛"
        },
        {
            "adcode": "620100",
            "city": "兰州"
        },
        {
            "adcode": "620200",
            "city": "嘉峪关"
        },
        {
            "adcode": "620300",
            "city": "金昌"
        },
        {
            "adcode": "620400",
            "city": "白银"
        },
        {
            "adcode": "620500",
            "city": "天水"
        },
        {
            "adcode": "620600",
            "city": "武威"
        },
        {
            "adcode": "620700",
            "city": "张掖"
        },
        {
            "adcode": "620800",
            "city": "平凉"
        },
        {
            "adcode": "620900",
            "city": "酒泉"
        },
        {
            "adcode": "621000",
            "city": "庆阳"
        },
        {
            "adcode": "621100",
            "city": "定西"
        },
        {
            "adcode": "621200",
            "city": "陇南"
        },
        {
            "adcode": "622900",
            "city": "临夏"
        },
        {
            "adcode": "623000",
            "city": "甘南"
        },
        {
            "adcode": "630100",
            "city": "西宁"
        },
        {
            "adcode": "630200",
            "city": "海东"
        },
        {
            "adcode": "632200",
            "city": "海北"
        },
        {
            "adcode": "632300",
            "city": "黄南"
        },
        {
            "adcode": "632500",
            "city": "海南"
        },
        {
            "adcode": "632600",
            "city": "果洛"
        },
        {
            "adcode": "632700",
            "city": "玉树"
        },
        {
            "adcode": "632800",
            "city": "海西"
        },
        {
            "adcode": "640100",
            "city": "银川"
        },
        {
            "adcode": "640200",
            "city": "石嘴山"
        },
        {
            "adcode": "640300",
            "city": "吴忠"
        },
        {
            "adcode": "640400",
            "city": "固原"
        },
        {
            "adcode": "640500",
            "city": "中卫"
        },
        {
            "adcode": "650100",
            "city": "乌鲁木齐"
        },
        {
            "adcode": "650200",
            "city": "克拉玛依"
        },
        {
            "adcode": "650400",
            "city": "吐鲁番"
        },
        {
            "adcode": "650500",
            "city": "哈密"
        },
        {
            "adcode": "652300",
            "city": "昌吉"
        },
        {
            "adcode": "652700",
            "city": "博尔塔拉"
        },
        {
            "adcode": "652800",
            "city": "巴音郭楞"
        },
        {
            "adcode": "652900",
            "city": "阿克苏"
        },
        {
            "adcode": "653000",
            "city": "克孜勒苏"
        },
        {
            "adcode": "653100",
            "city": "喀什"
        },
        {
            "adcode": "653200",
            "city": "和田"
        },
        {
            "adcode": "654000",
            "city": "伊犁"
        },
        {
            "adcode": "654200",
            "city": "塔城"
        },
        {
            "adcode": "654300",
            "city": "阿勒泰"
        },
        {
            "adcode": "659001",
            "city": "石河子"
        },
        {
            "adcode": "659002",
            "city": "阿拉尔"
        },
        {
            "adcode": "659003",
            "city": "图木舒克"
        },
        {
            "adcode": "659004",
            "city": "五家渠"
        },
        {
            "adcode": "659005",
            "city": "北屯"
        },
        {
            "adcode": "659006",
            "city": "铁门关"
        },
        {
            "adcode": "659007",
            "city": "双河"
        },
        {
            "adcode": "659008",
            "city": "可克达拉"
        },
        {
            "adcode": "659009",
            "city": "昆玉"
        },
        {
            "adcode": "410100",
            "city": "郑州"
        },
        {
            "adcode": "410200",
            "city": "开封"
        },
        {
            "adcode": "410300",
            "city": "洛阳"
        },
        {
            "adcode": "410400",
            "city": "平顶山"
        },
        {
            "adcode": "410500",
            "city": "安阳"
        },
        {
            "adcode": "410600",
            "city": "鹤壁"
        },
        {
            "adcode": "410700",
            "city": "新乡"
        },
        {
            "adcode": "410800",
            "city": "焦作"
        },
        {
            "adcode": "410900",
            "city": "濮阳"
        },
        {
            "adcode": "411000",
            "city": "许昌"
        },
        {
            "adcode": "411100",
            "city": "漯河"
        },
        {
            "adcode": "411200",
            "city": "三门峡"
        },
        {
            "adcode": "411300",
            "city": "南阳"
        },
        {
            "adcode": "411400",
            "city": "商丘"
        },
        {
            "adcode": "411500",
            "city": "信阳"
        },
        {
            "adcode": "411600",
            "city": "周口"
        },
        {
            "adcode": "411700",
            "city": "驻马店"
        },
        {
            "adcode": "419001",
            "city": "济源"
        },
        {
            "adcode": "420100",
            "city": "武汉"
        },
        {
            "adcode": "420200",
            "city": "黄石"
        },
        {
            "adcode": "420300",
            "city": "十堰"
        },
        {
            "adcode": "420500",
            "city": "宜昌"
        },
        {
            "adcode": "420600",
            "city": "襄阳"
        },
        {
            "adcode": "420700",
            "city": "鄂州"
        },
        {
            "adcode": "420800",
            "city": "荆门"
        },
        {
            "adcode": "420900",
            "city": "孝感"
        },
        {
            "adcode": "421000",
            "city": "荆州"
        },
        {
            "adcode": "421100",
            "city": "黄冈"
        },
        {
            "adcode": "421200",
            "city": "咸宁"
        },
        {
            "adcode": "421300",
            "city": "随州"
        },
        {
            "adcode": "422800",
            "city": "恩施"
        },
        {
            "adcode": "429004",
            "city": "仙桃"
        },
        {
            "adcode": "429005",
            "city": "潜江"
        },
        {
            "adcode": "429006",
            "city": "天门"
        },
        {
            "adcode": "429021",
            "city": "神农架"
        },
        {
            "adcode": "430100",
            "city": "长沙"
        },
        {
            "adcode": "430200",
            "city": "株洲"
        },
        {
            "adcode": "430300",
            "city": "湘潭"
        },
        {
            "adcode": "430400",
            "city": "衡阳"
        },
        {
            "adcode": "430500",
            "city": "邵阳"
        },
        {
            "adcode": "430600",
            "city": "岳阳"
        },
        {
            "adcode": "430700",
            "city": "常德"
        },
        {
            "adcode": "430800",
            "city": "张家界"
        },
        {
            "adcode": "430900",
            "city": "益阳"
        },
        {
            "adcode": "431000",
            "city": "郴州"
        },
        {
            "adcode": "431100",
            "city": "永州"
        },
        {
            "adcode": "431200",
            "city": "怀化"
        },
        {
            "adcode": "431300",
            "city": "娄底"
        },
        {
            "adcode": "433100",
            "city": "湘西"
        },
        {
            "adcode": "130100",
            "city": "石家庄"
        },
        {
            "adcode": "130200",
            "city": "唐山"
        },
        {
            "adcode": "130300",
            "city": "秦皇岛"
        },
        {
            "adcode": "130400",
            "city": "邯郸"
        },
        {
            "adcode": "130500",
            "city": "邢台"
        },
        {
            "adcode": "130600",
            "city": "保定"
        },
        {
            "adcode": "130700",
            "city": "张家口"
        },
        {
            "adcode": "130800",
            "city": "承德"
        },
        {
            "adcode": "130900",
            "city": "沧州"
        },
        {
            "adcode": "131000",
            "city": "廊坊"
        },
        {
            "adcode": "131100",
            "city": "衡水"
        },
        {
            "adcode": "140100",
            "city": "太原"
        },
        {
            "adcode": "140200",
            "city": "大同"
        },
        {
            "adcode": "140300",
            "city": "阳泉"
        },
        {
            "adcode": "140400",
            "city": "长治"
        },
        {
            "adcode": "140500",
            "city": "晋城"
        },
        {
            "adcode": "140600",
            "city": "朔州"
        },
        {
            "adcode": "140700",
            "city": "晋中"
        },
        {
            "adcode": "140800",
            "city": "运城"
        },
        {
            "adcode": "140900",
            "city": "忻州"
        },
        {
            "adcode": "141000",
            "city": "临汾"
        },
        {
            "adcode": "141100",
            "city": "吕梁"
        },
        {
            "adcode": "150100",
            "city": "呼和浩特"
        },
        {
            "adcode": "150200",
            "city": "包头"
        },
        {
            "adcode": "150300",
            "city": "乌海"
        },
        {
            "adcode": "150400",
            "city": "赤峰"
        },
        {
            "adcode": "150500",
            "city": "通辽"
        },
        {
            "adcode": "150600",
            "city": "鄂尔多斯"
        },
        {
            "adcode": "150700",
            "city": "呼伦贝尔"
        },
        {
            "adcode": "150800",
            "city": "巴彦淖尔"
        },
        {
            "adcode": "150900",
            "city": "乌兰察布"
        },
        {
            "adcode": "152200",
            "city": "兴安"
        },
        {
            "adcode": "152500",
            "city": "锡林郭勒"
        },
        {
            "adcode": "152900",
            "city": "阿拉善"
        },
        {
            "adcode": "440100",
            "city": "广州"
        },
        {
            "adcode": "440200",
            "city": "韶关"
        },
        {
            "adcode": "440300",
            "city": "深圳"
        },
        {
            "adcode": "440400",
            "city": "珠海"
        },
        {
            "adcode": "440500",
            "city": "汕头"
        },
        {
            "adcode": "440600",
            "city": "佛山"
        },
        {
            "adcode": "440700",
            "city": "江门"
        },
        {
            "adcode": "440800",
            "city": "湛江"
        },
        {
            "adcode": "440900",
            "city": "茂名"
        },
        {
            "adcode": "441200",
            "city": "肇庆"
        },
        {
            "adcode": "441300",
            "city": "惠州"
        },
        {
            "adcode": "441400",
            "city": "梅州"
        },
        {
            "adcode": "441500",
            "city": "汕尾"
        },
        {
            "adcode": "441600",
            "city": "河源"
        },
        {
            "adcode": "441700",
            "city": "阳江"
        },
        {
            "adcode": "441800",
            "city": "清远"
        },
        {
            "adcode": "441900",
            "city": "东莞"
        },
        {
            "adcode": "442000",
            "city": "中山"
        },
        {
            "adcode": "445100",
            "city": "潮州"
        },
        {
            "adcode": "445200",
            "city": "揭阳"
        },
        {
            "adcode": "445300",
            "city": "云浮"
        },
        {
            "adcode": "450100",
            "city": "南宁"
        },
        {
            "adcode": "450200",
            "city": "柳州"
        },
        {
            "adcode": "450300",
            "city": "桂林"
        },
        {
            "adcode": "450400",
            "city": "梧州"
        },
        {
            "adcode": "450500",
            "city": "北海"
        },
        {
            "adcode": "450600",
            "city": "防城港"
        },
        {
            "adcode": "450700",
            "city": "钦州"
        },
        {
            "adcode": "450800",
            "city": "贵港"
        },
        {
            "adcode": "450900",
            "city": "玉林"
        },
        {
            "adcode": "451000",
            "city": "百色"
        },
        {
            "adcode": "451100",
            "city": "贺州"
        },
        {
            "adcode": "451200",
            "city": "河池"
        },
        {
            "adcode": "451300",
            "city": "来宾"
        },
        {
            "adcode": "451400",
            "city": "崇左"
        },
        {
            "adcode": "510100",
            "city": "成都"
        },
        {
            "adcode": "510300",
            "city": "自贡"
        },
        {
            "adcode": "510400",
            "city": "攀枝花"
        },
        {
            "adcode": "510500",
            "city": "泸州"
        },
        {
            "adcode": "510600",
            "city": "德阳"
        },
        {
            "adcode": "510700",
            "city": "绵阳"
        },
        {
            "adcode": "510800",
            "city": "广元"
        },
        {
            "adcode": "510900",
            "city": "遂宁"
        },
        {
            "adcode": "511000",
            "city": "内江"
        },
        {
            "adcode": "511100",
            "city": "乐山"
        },
        {
            "adcode": "511300",
            "city": "南充"
        },
        {
            "adcode": "511400",
            "city": "眉山"
        },
        {
            "adcode": "511500",
            "city": "宜宾"
        },
        {
            "adcode": "511600",
            "city": "广安"
        },
        {
            "adcode": "511700",
            "city": "达州"
        },
        {
            "adcode": "511800",
            "city": "雅安"
        },
        {
            "adcode": "511900",
            "city": "巴中"
        },
        {
            "adcode": "512000",
            "city": "资阳"
        },
        {
            "adcode": "513200",
            "city": "阿坝"
        },
        {
            "adcode": "513300",
            "city": "甘孜"
        },
        {
            "adcode": "513400",
            "city": "凉山"
        },
        {
            "adcode": "520100",
            "city": "贵阳"
        },
        {
            "adcode": "520200",
            "city": "六盘水"
        },
        {
            "adcode": "520300",
            "city": "遵义"
        },
        {
            "adcode": "520400",
            "city": "安顺"
        },
        {
            "adcode": "520500",
            "city": "毕节"
        },
        {
            "adcode": "520600",
            "city": "铜仁"
        },
        {
            "adcode": "522300",
            "city": "黔西南"
        },
        {
            "adcode": "522600",
            "city": "黔东南"
        },
        {
            "adcode": "522700",
            "city": "黔南"
        },
        {
            "adcode": "530100",
            "city": "昆明"
        },
        {
            "adcode": "530300",
            "city": "曲靖"
        },
        {
            "adcode": "530400",
            "city": "玉溪"
        },
        {
            "adcode": "530500",
            "city": "保山"
        },
        {
            "adcode": "530600",
            "city": "昭通"
        },
        {
            "adcode": "530700",
            "city": "丽江"
        },
        {
            "adcode": "530800",
            "city": "普洱"
        },
        {
            "adcode": "530900",
            "city": "临沧"
        },
        {
            "adcode": "532300",
            "city": "楚雄"
        },
        {
            "adcode": "532500",
            "city": "红河"
        },
        {
            "adcode": "532600",
            "city": "文山"
        },
        {
            "adcode": "532800",
            "city": "西双版纳"
        },
        {
            "adcode": "532900",
            "city": "大理"
        },
        {
            "adcode": "533100",
            "city": "德宏"
        },
        {
            "adcode": "533300",
            "city": "怒江"
        },
        {
            "adcode": "533400",
            "city": "迪庆"
        },
        {
            "adcode": "540100",
            "city": "拉萨"
        },
        {
            "adcode": "540200",
            "city": "日喀则"
        },
        {
            "adcode": "540300",
            "city": "昌都"
        },
        {
            "adcode": "540400",
            "city": "林芝"
        },
        {
            "adcode": "540500",
            "city": "山南"
        },
        {
            "adcode": "540600",
            "city": "那曲"
        },
        {
            "adcode": "542500",
            "city": "阿里"
        },
        {
            "adcode": "500000",
            "city": "重庆"
        },
        {
            "adcode": "120000",
            "city": "天津"
        },
        {
            "adcode": "110000",
            "city": "北京"
        },
        {
            "adcode": "310000",
            "city": "上海"
        }]

    # bidMethodList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    orgTypeList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    bidProcesseList = [20, 40, 50, 100, 60, 70, 80, 90, 3]
    # bidIndustryList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]


    count = 0
    for i in range(len(adcodes)):
        item = adcodes[i]

        name = item['city']
        adcode = item['adcode']

        # for bidMethod in bidMethodList:
        for orgType in orgTypeList:
            for bidProcesse in bidProcesseList:
                # for bidIndustry in bidIndustryList:

                    data = {
                        'page': 1,
                        'count': 29,
                        'date': f'{yesterday}_{yesterday}',
                        'adcodes': adcode,
                        # 'bidMethods': bidMethod,
                        'orgTypes': orgType,
                        'bidProcesses': bidProcesse,
                        # 'bidIndustry': bidIndustry

                    }
                    print(count, data)
                    count += 1
                    moenApp.send_task('bid.jianyu.zl_search', args=(json.dumps(data),))
                    # if i > 2:
                    #     break


def send_zl_search_keyword():


    key_list = rds_206_11.smembers('jianyu:9w_keyword') # 这个keyword_1里面是过滤了一遍的
    for key in key_list:
        key = key.decode()
        print(key)
        params = {
            'page': 1,
            'count': 29,
            'keyword': key,
        }

        moenApp.send_task('bid.jianyu.zl_search_keyword', args=(json.dumps(params),))


if __name__ == '__main__':
    send_jianyu_keyword()
    send_zl_search()
    send_zl_search_keyword()
    print(datetime.datetime.now())
