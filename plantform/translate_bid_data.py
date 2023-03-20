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
import platform


if 'Linux' == platform.system():
    print('Linux 平台')
    source_topic = 'spider_bid_clean_v1'
    TEST = False


else:
    print(f'测试环境: {platform.system()}')
    source_topic = 'spider_bid_clean_test_v1'
    TEST = True



target_topic = 'spider_bid'

bootstrap_servers = ['172.16.63.83:9092', '172.16.113.148:9092', '172.16.135.145:9092']

class Translate:
    def __init__(self, data={}):
        self.data = data
        self.consumer = KafkaConsumer(source_topic,
                                 group_id='my-group',
                                 # auto_offset_reset='smallest',
                                 value_deserializer=lambda m: json.loads(m.decode('ascii')),
                                 # consumer_timeout_ms=1000,
                                 bootstrap_servers=bootstrap_servers)

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            # value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

    def send(self, params):

        sf = SonyFlake()
        next_id = sf.next_id()

        final_data = {
            "version": 1,
            "trace_sn": str(next_id),
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + time.strftime('%z',
                                                                                                       time.localtime()),
            "data_type": "spider_bid",
            "data": params
        }

        parmas_message = json.dumps(final_data, ensure_ascii=False)
        v = parmas_message.encode('utf-8')

        self.producer.send(target_topic, v,).add_callback(self.on_send_success).add_errback(self.on_send_error)
        self.producer.flush()
        # 打印成功发送的信息
        # self.producer.close()

    def on_send_success(self, record_metadata):
        print("发送到：topic:{} partition:{} offset:{}".format(record_metadata.topic, record_metadata.partition,
                                                       record_metadata.offset))

    def on_send_error(self, excp):
        print(excp)

    # consumer.seek(TopicPartition(topic='spider-bid-info-v1', partition=0), 13)

    def run(self):
        for message in self.consumer:
            print ("读取到：%s:%d:%d" % (message.topic, message.partition,
                                              message.offset
                                              ))
            self.data = message.value.get('data')
            if not self.data:
                print(f'没有读取到data:{message}')
                continue
            try:
                self.check()
                if not TEST:
                    self.send(self.data)  # 测试不发送

            except Exception as e:
                print(f'error:{e},,data:{self.data}')


    def check(self):
        self.check_uuid()
        self.check_title()
        self.check_notice_type()
        self.check_bid_type()
        self.check_bidding_type()
        self.check_invite_company()
        self.check_win_company()
        self.check_agency_company()
        self.check_pub_province()
        self.check_pub_city()
        self.check_pub_district()
        self.check_pub_addr()
        self.check_pub_time()
        self.check_tender_time()
        self.check_item_number()
        self.check_products()
        self.check_money()
        self.check_unit()
        self.check_notice_detail()
        self.check_url()
        self.check_doc()
        self.check_source_name()
        self.check_other()
        self.check_filepath()

        # print(json.dumps(self.data))

    def check_uuid(self):
        uuid = self.data.get('uuid')
        if not uuid:
            raise ValueError('no uuid')

    def check_title(self):
        title = self.data.get('title')
        if not title:
            raise ValueError('no title')

    def check_notice_type(self):
        notice_type = self.data.get('notice_type')
        if not notice_type:
            self.data['notice_type'] = 1


    def check_bid_type(self):
        bid_type = self.data.get('bid_type')
        if not bid_type:
            self.data['bid_type'] = ''

    def check_bidding_type(self):
        bidding_type = self.data.get('bidding_type')
        if not bidding_type:
            self.data['bidding_type'] = ''

    def check_invite_company(self):
        invite_company = self.data.get('invite_company')
        if not invite_company:
            self.data['invite_company'] = ''

    def check_win_company(self):
        win_company = self.data.get('win_company')
        if not win_company:
            self.data['win_company'] = ''

    def check_agency_company(self):
        agency_company = self.data.get('agency_company')
        if not agency_company:
            self.data['agency_company'] = ''

    def check_pub_province(self):
        pub_province = self.data.get('pub_province')
        if not pub_province:
            self.data['pub_province'] = ''

    def check_pub_city(self):
        pub_city = self.data.get('pub_city')
        if not pub_city:
            self.data['pub_city'] = ''

    def check_pub_district(self):
        pub_district = self.data.get('pub_district')
        if not pub_district:
            self.data['pub_district'] = ''

    def check_pub_addr(self):
        pub_addr = self.data.get('pub_addr')
        if not pub_addr:
            self.data['pub_addr'] = ''

    def check_pub_time(self):
        pub_time = self.data.get('pub_time')
        if not pub_time:
            self.data['pub_addr'] = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))

    def check_tender_time(self):
        tender_time = self.data.get('tender_time')
        if not tender_time:
            self.data['tender_time'] = 31507200000

    def check_item_number(self):
        item_number = self.data.get('item_number')
        if not item_number:
            self.data['item_number'] = ''

    def check_products(self):
        products = self.data.get('products')
        if not products:
            self.data['products'] = ''

    def check_money(self):
        money = self.data.get('money')
        if not money:
            self.data['money'] = ''

    def check_unit(self):
        unit = self.data.get('unit')
        if not unit:
            self.data['unit'] = '元'

    def check_notice_detail(self):
        notice_detail = self.data.get('notice_detail')
        if not notice_detail:
            self.data['notice_detail'] = ''

    def check_url(self):
        url = self.data.get('url')
        if not url:
            self.data['url'] = ''

    def check_doc(self):
        doc = self.data.get('doc')
        if not doc:
            self.data['doc'] = ''

    def check_source_name(self):
        source_name = self.data.get('source_name')
        print(f'数据来自网站：{source_name}')
        if not source_name:
            # self.data['source_name'] = '未知'
            raise ValueError('no source_name')
    def check_other(self):
        other = self.data.get('other')
        if not other:
            self.data['other'] = ''

    def check_filepath(self):
        filepath = self.data.get('filepath')
        if not filepath:
            # self.data['filepath'] = ''
            raise ValueError('no filepath')


# consume earliest available messages, don't commit offsets
# KafkaConsumer(auto_offset_reset='earliest', enable_auto_commit=False)

# consume json messages
# KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('ascii')))


if __name__ == '__main__':
    # tran.run()
    data = {
        'uuid': '6831ce0c8e721da4febe98439cb6765e',
        'title': '徐州经济技术开发区珑越东方配套市政道路工程;',
        'notice_type': 1,
        'bid_type': '招标公告',
        'pub_province': '江苏省',
        'pub_city': '',
        'pub_district': '',
        'pub_time': '2023-02-15',
        'notice_detail': '<table id="Table1" bordercolor="#a9d7e8" cellspacing="0" cellpadding="5" width="750" align="center" bgcolor="#ffffff" border="1">\r\n                            <tr>\r\n                                <td bgcolor="#fbfdfe" colspan="4" height="2" align="center"><font size="4" color="red" face="宋体-方正超大字符集"><b>[0]徐州经济技术开发区珑越东方配套市政道路工程的招标公告</b></font></td>\r\n                            </tr>\r\n                            <tr>\r\n                                <td align="center" bgcolor="#e5f2fa" nowrap>项目编号</td>\r\n                                <td align="left">\r\n                                    <span id="ProjectBH_23" style="display:inline-block;width:97%;">E3203010319005778</span></td>\r\n                                <td align="center" bgcolor="#e5f2fa" nowrap>项目名称</td>\r\n                                <td align="left">\r\n                                    <span id="ProjectName_23" style="display:inline-block;width:97%;">徐州经济技术开发区珑越东方配套市政道路工程</span></td>\r\n                            </tr>\r\n                            <tr>\r\n                                <td align="center" bgcolor="#e5f2fa" nowrap>标段编号</td>\r\n                                <td align="left">\r\n                                    <span id="BiaoDuanNO_23" style="display:inline-block;width:97%;">E3203010319005778001001;</span></td>\r\n                                <td align="center" bgcolor="#e5f2fa" nowrap>标段名称</td>\r\n                                <td align="left">\r\n                                    <span id="BiaoDuanName_23" style="display:inline-block;width:97%;">徐州经济技术开发区珑越东方配套市政道路工程;</span></td>\r\n                            </tr>\r\n                            <tr id="Tr3">\r\n\t<td align="center" bgcolor="#e5f2fa" nowrap>招标人名称</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="ZaoBiaoRen_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr4" nowrap>\r\n\t<td align="center" bgcolor="#e5f2fa">代理机构名称</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="jgmc_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr5" nowrap>\r\n\t<td align="center" bgcolor="#e5f2fa">项目批准机关名称</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="PiZhunBM_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr6">\r\n\t<td align="center" bgcolor="#e5f2fa" nowrap>工程所须资金来源</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="MoneySourse_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr7">\r\n\t<td align="center" bgcolor="#e5f2fa" nowrap>工程地点</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="ProjectAddress_23" designtimedragdrop="560" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr8">\r\n\t<td align="center" bgcolor="#e5f2fa" nowrap>工程规模</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="GongChenGM_23" designtimedragdrop="563" style="display:inline-block;width:575px;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr9">\r\n\t<td class="Table_special_Mis1" align="center" colspan="4" height="30" bgcolor="#e5f2fa">标段具体信息</td>\r\n</tr>\r\n\r\n                            <tr id="Tr10">\r\n\t<td align="center" colspan="4">\r\n                                    </td>\r\n</tr>\r\n\r\n                            <tr id="Tr11">\r\n\t<td align="center" bgcolor="#e5f2fa">申请人可申请的最多标段数</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="mostBMBDS_23" style="display:inline-block;width:76px;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr12">\r\n\t<td align="center" bgcolor="#e5f2fa">报名地点</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="BaoMingAddress_23" style="display:inline-block;width:100%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr13">\r\n\t<td align="center" bgcolor="#e5f2fa">公告发布日期</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="lblFBDate"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr14">\r\n\t<td align="center" bgcolor="#e5f2fa">计划开工时间</td>\r\n\t<td align="left">\r\n                                    <span id="PlanKGDate_23" style="display:inline-block;width:120px;"></span></td>\r\n\t<td align="center" bgcolor="#e5f2fa">计划竣工时间</td>\r\n\t<td align="left">\r\n                                    <span id="PlanJGDate_23" style="display:inline-block;width:120px;"></span></td>\r\n</tr>\r\n\r\n                            <tr>\r\n                                <td align="center" bgcolor="#e5f2fa">公告开始时间</td>\r\n                                <td align="left">\r\n                                    <span id="RptStartDate_23" style="display:inline-block;width:120px;">2023年2月15日</span></td>\r\n                                <td align="center" bgcolor="#e5f2fa">公告结束时间</td>\r\n                                <td align="left">\r\n                                    <span id="RptEndDate_23" style="display:inline-block;width:120px;">2023年2月28日</span></td>\r\n                            </tr>\r\n\r\n                            <tr>\r\n                                <td align="center" bgcolor="#e5f2fa" nowrap>工程类型</td>\r\n                                <td align="left">\r\n                                    <span id="ZB_Type_23" style="display:inline-block;width:97%;">市政工程施工</span></td>\r\n                                \r\n                            </tr>\r\n\r\n                            <tr id="Tr16">\r\n\t<td class="Table_special_Mis1" align="center" colspan="4" height="30" bgcolor="#e5f2fa">申请人应当具备的主要资格条件</td>\r\n</tr>\r\n\r\n                            <tr id="trZzDj1">\r\n\t<td align="center" bgcolor="#e5f2fa">申请人资质类别和等级</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="lblShenQiRenZzDj" style="display:inline-block;height:100%;width:100%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="trZzDj2">\r\n\t<td align="center" bgcolor="#e5f2fa">拟选报名人员资质等级</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="XiangMuJL_DJ_23" style="display:inline-block;height:100%;width:100%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="trZzDj3">\r\n\t<td align="center" bgcolor="#e5f2fa">企业业绩、信誉</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="Ete_Achieve_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="trZzDj4">\r\n\t<td align="center" bgcolor="#e5f2fa">项目经理(总监)/建造师业绩、信誉</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="XiangMuJL_Achieve_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="trZzDj5">\r\n\t<td align="center" bgcolor="#e5f2fa">其他条件</td>\r\n\t<td align="left" colspan="3">\r\n                                    <span id="OtherAchieve_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="trzygg" style="DISPLAY: none">\r\n\t<td align="center" bgcolor="#e5f2fa">公告信息</td>\r\n\t<td align="left" colspan="3"><span id="zygg_kkk">1.招标条件 <br>\r\n本招标项目徐州经济技术开发区珑越东方配套市政道路工程已由徐州经济技术开发区管委会以徐开管项[2023]6号批准建设，项目业主为徐州经济技术开发区投资项目代建中心，建设资金来自由财政等多渠道统筹解决，项目出资比例为 100% 。项目已具备招标条件，现对该项目 徐州经济技术开发区珑越东方配套市政道路工程 的施工进行公开招标，特邀请有兴趣的潜在投标人参加投标。 <br>\r\n2.工程概况与招标范围 <br>\r\n2.1工程概况 <br>\r\n2.1.1建设地点：徐州经济技术开发区金龙湖街道。 <br>\r\n2.1.2建设规模：珑越东路以西，凤翔路以南，和平大道以北，工程起点接现状A线车行道边，桩号为K0+006.959，工程终点接珑樾东路交叉口，桩号为K0+328.362，长度约321.403m，红线宽度20m。珑越东路：珑越北路以东，高新路以西，凤翔路以南，和平大道以北，工程起点接现状凤翔路车行道边，桩号为K0+007.578，工程终点接现状和平大道车行道边，桩号为K0+308.06，长度约300.482m，红线宽度20m。 <br>\r\n建设内容包括：路基工程、路面工程、雨水、污水等管网排水工程及路灯及其他附属设施等。 <br>\r\n2.1.3合同估算价：约1153.17万元； <br>\r\n2.1.4工期要求：90日历天； <br>\r\n2.1.5其他:本工程共分壹个标段。 <br>\r\n2.2招标范围：包括路基工程、路面工程、雨水、污水等管网排水工程及路灯及其他附属设施等。详见施工图及工程量清单内容。 <br>\r\n3.投标人资格要求 <br>\r\n3.1投标人须具备独立订立合同的能力，且具备市政公用工程施工总承包叁级（含）以上资质，安全生产许可证，并在人员、设备、资金等方面具有相应的施工能力。 <br>\r\n3.2投标人拟派项目负责人须具备：市政公用工程专业贰级注册建造师，《建筑施工企业安全生产考核合格证书》（B证），且必须满足下列条件： <br>\r\n（1）项目负责人不得同时在两个或者两个以上单位受聘或者执业（是指：a.同时在两个及以上单位签订劳动合同或交纳社会保险；b.将本人执（职）业资格证书同时注册在两个及以上单位）。 <br>\r\n（2）项目负责人是非变更后无在建工程，或项目负责人是变更后无在建工程（必须原合同工期已满且变更备案之日已满6个月），或因非承包方原因致使工程项目停工或因故不能按期开工、且已办理了项目负责人解锁手续，或项目负责人有在建工程，但该在建工程与本次招标的工程属于同一工程项目、同一项目批文、同一施工地点分段发包或分期施工的情况且总的工程规模在项目负责人执业范围之内。项目负责人不得在其他项目中担任项目负责人、技术负责人、质检员、安全员、施工员任一职务（已在绿化养护、市政养护工程中担任项目负责人、技术负责人、质检员、安全员、施工员视为有在建工程）。 <br>\r\n（3）项目负责人无行贿犯罪行为记录；或有行贿犯罪行为记录，但自记录之日起已超过5年的。 <br>\r\n3.3投标人不得有招标文件第二章投标人须知第1.4.3项规定的情形。 <br>\r\n3.4 本次招标不接受联合体投标。 <br>\r\n3.5 投标人在递交投标文件截止时间前须取得《徐州市建筑业企业信用管理手册》。 <br>\r\n3.6失信被执行人惩戒执行《关于在公共资源交易领域的招标投标活动中建立对失信被执行人联合惩戒机制的实施意见》（苏信用办〔2018〕23号）。 <br>\r\n3.7 本工程实行电子化招投标，投标人及拟选派项目负责人（注册建造师）必须在投标文件递交截止时间前已在“徐州市建筑市场监管与诚信信息一体化工作平台”中备案。 <br>\r\n3.8 根根据《省住房城乡建设关于开展建筑业企业资质动态监管工作的公告》（〔2018〕第6号）、《省住房城乡建设为于建筑业企业资质动态监管不合格企业参加招投标相关事宜的复函》（苏建函建管 〔2019〕233号），资格审查时，若投标人在投标截止时间前投标人资格要求资质的核查结果为不达标，仍在公示期的，将作为资格审查不通过处理。（企业动态资质查询信息以江苏省建筑市场监管与诚信信息一体化平台发布的信息为准）。 <br>\r\n4. 招标文件的获取 <br>\r\n4.1招标文件获取时间为：2023年2月15日至2023年2月28日09时30分； <br>\r\n4.2招标文件获取方式：投标人使用“江苏CA数字证书”登录“电子招标投标交易平台”获取； <br>\r\n本招标公告及招标文件中“电子招标投标交易平台”是指：徐州电子化招投标系统（http://218.3.177.168/xzhynew/）； <br>\r\n5. 投标截止时间 <br>\r\n5.1 投标截止时间为 ：2023年2月28日09时30分。 <br>\r\n5.2逾期送达的投标文件，招标人不予受理。 <br>\r\n6. 资格审查 <br>\r\n本次招标采用资格后审方式进行资格审查，资格评审标准详见招标文件第三章。   <br>\r\n7. 开标方式 <br>\r\n本工程采用不见面开标方式。在开标过程如遇到问题，请及时联系技术支持客服电话，电话为：4009980000。 <br>\r\n8. 评标方法 <br>\r\n本次招标采用 合理低价法 ，评标标准和方法详见招标文件第三章。 <br>\r\n9. 发布公告的媒介 <br>\r\n本次招标公告在江苏省建设工程招标网（http://www.jszb.com.cn/jszb/）、徐州市公共资源交易网（http://ggzy.zwb.xz.gov.cn/index.html）上发布。 <br>\r\n10. 联系方式 <br>\r\n招 标 人：徐州经济技术开发区投资项目代建中心 <br>\r\n地    址：徐州经济技术开发区科技大厦7楼 <br>\r\n联 系 人：付用笛 <br>\r\n电    话：0516-83255008 <br>\r\n招标代理机构：南京建淳造价师事务所有限公司 <br>\r\n地    址：徐州市云龙区民主南路时代广场C座2602室 <br>\r\n联 系 人：崔兴俊 <br>\r\n电    话：0516-83331020 <br>\r\n电子邮箱：361779287@qq.com <br>\r\n2023年2月15日</span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr17">\r\n\t<td class="Table_special_Mis1" align="center" colspan="4" height="30" bgcolor="#e5f2fa">招标人联系方式</td>\r\n</tr>\r\n\r\n                            <tr id="Tr18">\r\n\t<td style="HEIGHT: 26px" align="center" bgcolor="#e5f2fa" width="15%">地址</td>\r\n\t<td style="HEIGHT: 26px" align="left" width="35%">\r\n                                    <span id="ZBR_Address_23" style="display:inline-block;width:97%;"></span></td>\r\n\t<td style="HEIGHT: 26px" align="left" bgcolor="#e5f2fa" width="15%">\r\n                                    <p align="center">联系人</p>\r\n                                </td>\r\n\t<td align="left" width="35%">\r\n                                    <span id="ZBR_LXR_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr19">\r\n\t<td align="center" bgcolor="#e5f2fa">传真</td>\r\n\t<td align="left">\r\n                                    <span id="ZBR_Fax_23" style="display:inline-block;width:97%;"></span></td>\r\n\t<td bgcolor="#e5f2fa">\r\n                                    <p align="center">电话</p>\r\n                                </td>\r\n\t<td align="left">\r\n                                    <span id="ZBR_Tel_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr15">\r\n\t<td align="center" bgcolor="#e5f2fa">邮编</td>\r\n\t<td align="left">\r\n                                    <span id="ZBR_PostCode_23" style="display:inline-block;width:97%;"></span></td>\r\n\t<td align="center" bgcolor="#e5f2fa">E－mail</td>\r\n\t<td align="left">\r\n                                    <span id="ZBR_Email_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="trDLJG1" bgcolor="#e5f2fa">\r\n\t<td class="Table_special_Mis1" align="center" colspan="4" height="30">招标代理机构联系方式</td>\r\n</tr>\r\n\r\n                            <tr id="trDLJG2">\r\n\t<td align="center" bgcolor="#e5f2fa">地址</td>\r\n\t<td align="left">\r\n                                    <span id="DL_Address_23" style="display:inline-block;width:97%;"></span></td>\r\n\t<td align="left" bgcolor="#e5f2fa">\r\n                                    <p align="center">联系人</p>\r\n                                </td>\r\n\t<td align="left">\r\n                                    <span id="DL_LXR_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="trDLJG3">\r\n\t<td align="center" bgcolor="#e5f2fa">传真</td>\r\n\t<td align="left">\r\n                                    <span id="DL_Fax_23" style="display:inline-block;width:97%;"></span></td>\r\n\t<td bgcolor="#e5f2fa">\r\n                                    <p align="center">电话</p>\r\n                                </td>\r\n\t<td align="left">\r\n                                    <span id="DL_Tel_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="trDLJG4">\r\n\t<td align="center" bgcolor="#e5f2fa">邮编</td>\r\n\t<td align="left">\r\n                                    <span id="DL_PostCode_23" style="display:inline-block;width:97%;"></span></td>\r\n\t<td align="center" bgcolor="#e5f2fa">E－mail</td>\r\n\t<td align="left">\r\n                                    <span id="DL_Email_23" style="display:inline-block;width:97%;"></span></td>\r\n</tr>\r\n\r\n                            <tr id="Tr2">\r\n\t<td align="center" bgcolor="#e5f2fa">报名信息</td>\r\n\t<td align="left" colspan="3">请申请人于 \r\n\t\t\t\t\t\t\t\t\t\t<span id="BM_Start_Date_23" style="display:inline-block;width:80px;"></span>至\r\n\t\t\t\t\t\t\t\t\t\t<span id="BM_End_Date_23" style="display:inline-block;width:90px;"></span>，每天上午\r\n\t\t\t\t\t\t\t\t\t\t<span id="SW_Start_Hour_23" style="display:inline-block;width:20px;"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="SW_Start_Minute_23" style="display:inline-block;width:20px;"></span>分 至\r\n\t\t\t\t\t\t\t\t\t\t<span id="SW_End_Hour_23" style="display:inline-block;width:20px;"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="SW_End_Minute_23" style="display:inline-block;width:20px;"></span>分，下午\r\n\t\t\t\t\t\t\t\t\t\t<span id="XW_Start_Hour_23" style="display:inline-block;width:20px;"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="XW_Start_Minute_23" style="display:inline-block;width:20px;"></span>分 至\r\n\t\t\t\t\t\t\t\t\t\t<span id="XW_End_Hour_23" style="display:inline-block;width:20px;"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="XW_End_Minute_23" style="display:inline-block;width:20px;"></span>分（公休日，节假日除外）到\r\n\t\t\t\t\t\t\t\t\t\t<u>\r\n                                            \r\n                                        </u> 报名，报名经办人须携带本人身份证件，并于\r\n\t\t\t\t\t\t\t\t\t\t<span id="ApplyStartDate_23" style="display:inline-block;width:90px;"></span>至\r\n\t\t\t\t\t\t\t\t\t\t<span id="ApplyEndDate_23" style="display:inline-block;width:90px;"></span>，每天上午\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQSW_Start_Hour_23" style="display:inline-block;width:20px;"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQSW_Start_Minute_23" style="display:inline-block;width:20px;"></span>分至\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQSW_End_Hour_23" style="display:inline-block;width:20px;"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQSW_End_Minute_23" style="display:inline-block;width:20px;"></span>分，下午\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQXW_Start_Hour_23" style="display:inline-block;width:20px;"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQXW_Start_Minute_23" style="display:inline-block;width:20px;"></span>分至\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQXW_End_Hour_23" style="display:inline-block;width:20px;"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQXW_End_Minute_23" style="display:inline-block;width:20px;"></span>分（公休日、节假日除外）到\r\n\t\t\t\t\t\t\t\t\t\t<u>\r\n                                            \r\n                                        </u>获取 <u>\r\n                                            <span id="WenJian_Type_23" style="display:inline-block;width:100px;"></span></u>。</td>\r\n</tr>\r\n\r\n                            <tr id="Tr1">\r\n\t<td colspan="4" style="DISPLAY: none">\r\n                                    <span id="FullTextSearch_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="ZiZhiDJ1_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="ZiZhiLB1_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="ZiZhiLB2_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="ZiZhiLB3_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="ZiZhiDJ2_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="ZiZhiDJ3_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="status_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="EP_Check_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="ZbdlQybm_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="DaiLiJiGouName_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="TianBaoFS_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="DaiLiJiGouCode_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="ZBRptBH_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="gg_Type_23" style="display:inline-block;width:25px;">特殊公告</span>\r\n                                    <span id="HuoQuWenJianAddress_23" style="display:inline-block;width:25px;"></span>\r\n                                    <span id="lblBianDuanShu"></span>\r\n                                    <span id="IsSecond_23">[0]</span>\r\n                                    <span id="zygg_Text_23">1.招标条件 <br>\r\n本招标项目徐州经济技术开发区珑越东方配套市政道路工程已由徐州经济技术开发区管委会以徐开管项[2023]6号批准建设，项目业主为徐州经济技术开发区投资项目代建中心，建设资金来自由财政等多渠道统筹解决，项目出资比例为 100% 。项目已具备招标条件，现对该项目 徐州经济技术开发区珑越东方配套市政道路工程 的施工进行公开招标，特邀请有兴趣的潜在投标人参加投标。 <br>\r\n2.工程概况与招标范围 <br>\r\n2.1工程概况 <br>\r\n2.1.1建设地点：徐州经济技术开发区金龙湖街道。 <br>\r\n2.1.2建设规模：珑越东路以西，凤翔路以南，和平大道以北，工程起点接现状A线车行道边，桩号为K0+006.959，工程终点接珑樾东路交叉口，桩号为K0+328.362，长度约321.403m，红线宽度20m。珑越东路：珑越北路以东，高新路以西，凤翔路以南，和平大道以北，工程起点接现状凤翔路车行道边，桩号为K0+007.578，工程终点接现状和平大道车行道边，桩号为K0+308.06，长度约300.482m，红线宽度20m。 <br>\r\n建设内容包括：路基工程、路面工程、雨水、污水等管网排水工程及路灯及其他附属设施等。 <br>\r\n2.1.3合同估算价：约1153.17万元； <br>\r\n2.1.4工期要求：90日历天； <br>\r\n2.1.5其他:本工程共分壹个标段。 <br>\r\n2.2招标范围：包括路基工程、路面工程、雨水、污水等管网排水工程及路灯及其他附属设施等。详见施工图及工程量清单内容。 <br>\r\n3.投标人资格要求 <br>\r\n3.1投标人须具备独立订立合同的能力，且具备市政公用工程施工总承包叁级（含）以上资质，安全生产许可证，并在人员、设备、资金等方面具有相应的施工能力。 <br>\r\n3.2投标人拟派项目负责人须具备：市政公用工程专业贰级注册建造师，《建筑施工企业安全生产考核合格证书》（B证），且必须满足下列条件： <br>\r\n（1）项目负责人不得同时在两个或者两个以上单位受聘或者执业（是指：a.同时在两个及以上单位签订劳动合同或交纳社会保险；b.将本人执（职）业资格证书同时注册在两个及以上单位）。 <br>\r\n（2）项目负责人是非变更后无在建工程，或项目负责人是变更后无在建工程（必须原合同工期已满且变更备案之日已满6个月），或因非承包方原因致使工程项目停工或因故不能按期开工、且已办理了项目负责人解锁手续，或项目负责人有在建工程，但该在建工程与本次招标的工程属于同一工程项目、同一项目批文、同一施工地点分段发包或分期施工的情况且总的工程规模在项目负责人执业范围之内。项目负责人不得在其他项目中担任项目负责人、技术负责人、质检员、安全员、施工员任一职务（已在绿化养护、市政养护工程中担任项目负责人、技术负责人、质检员、安全员、施工员视为有在建工程）。 <br>\r\n（3）项目负责人无行贿犯罪行为记录；或有行贿犯罪行为记录，但自记录之日起已超过5年的。 <br>\r\n3.3投标人不得有招标文件第二章投标人须知第1.4.3项规定的情形。 <br>\r\n3.4 本次招标不接受联合体投标。 <br>\r\n3.5 投标人在递交投标文件截止时间前须取得《徐州市建筑业企业信用管理手册》。 <br>\r\n3.6失信被执行人惩戒执行《关于在公共资源交易领域的招标投标活动中建立对失信被执行人联合惩戒机制的实施意见》（苏信用办〔2018〕23号）。 <br>\r\n3.7 本工程实行电子化招投标，投标人及拟选派项目负责人（注册建造师）必须在投标文件递交截止时间前已在“徐州市建筑市场监管与诚信信息一体化工作平台”中备案。 <br>\r\n3.8 根根据《省住房城乡建设关于开展建筑业企业资质动态监管工作的公告》（〔2018〕第6号）、《省住房城乡建设为于建筑业企业资质动态监管不合格企业参加招投标相关事宜的复函》（苏建函建管 〔2019〕233号），资格审查时，若投标人在投标截止时间前投标人资格要求资质的核查结果为不达标，仍在公示期的，将作为资格审查不通过处理。（企业动态资质查询信息以江苏省建筑市场监管与诚信信息一体化平台发布的信息为准）。 <br>\r\n4. 招标文件的获取 <br>\r\n4.1招标文件获取时间为：2023年2月15日至2023年2月28日09时30分； <br>\r\n4.2招标文件获取方式：投标人使用“江苏CA数字证书”登录“电子招标投标交易平台”获取； <br>\r\n本招标公告及招标文件中“电子招标投标交易平台”是指：徐州电子化招投标系统（http://218.3.177.168/xzhynew/）； <br>\r\n5. 投标截止时间 <br>\r\n5.1 投标截止时间为 ：2023年2月28日09时30分。 <br>\r\n5.2逾期送达的投标文件，招标人不予受理。 <br>\r\n6. 资格审查 <br>\r\n本次招标采用资格后审方式进行资格审查，资格评审标准详见招标文件第三章。   <br>\r\n7. 开标方式 <br>\r\n本工程采用不见面开标方式。在开标过程如遇到问题，请及时联系技术支持客服电话，电话为：4009980000。 <br>\r\n8. 评标方法 <br>\r\n本次招标采用 合理低价法 ，评标标准和方法详见招标文件第三章。 <br>\r\n9. 发布公告的媒介 <br>\r\n本次招标公告在江苏省建设工程招标网（http://www.jszb.com.cn/jszb/）、徐州市公共资源交易网（http://ggzy.zwb.xz.gov.cn/index.html）上发布。 <br>\r\n10. 联系方式 <br>\r\n招 标 人：徐州经济技术开发区投资项目代建中心 <br>\r\n地    址：徐州经济技术开发区科技大厦7楼 <br>\r\n联 系 人：付用笛 <br>\r\n电    话：0516-83255008 <br>\r\n招标代理机构：南京建淳造价师事务所有限公司 <br>\r\n地    址：徐州市云龙区民主南路时代广场C座2602室 <br>\r\n联 系 人：崔兴俊 <br>\r\n电    话：0516-83331020 <br>\r\n电子邮箱：361779287@qq.com <br>\r\n2023年2月15日</span>\r\n                                    <input name="hidPostBack" type="hidden" id="hidPostBack" style="WIDTH: 89px; HEIGHT: 22px" size="9"></td>\r\n</tr>\r\n\r\n                            <tr id="TrTZ" style="DISPLAY: none">\r\n\t<td align="center" bgcolor="#e5f2fa">报名信息</td>\r\n\t<td align="left" colspan="3">请申请人于 \r\n\t\t\t\t\t\t\t\t\t\t<span id="BM_Start_Date"></span>\r\n                                    <span id="SW_Start_Hour"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="SW_Start_Minute"></span>分，至\r\n\t\t\t\t\t\t\t\t\t\t<span id="BM_End_Date"></span>\r\n                                    <span id="XW_End_Hour"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="XW_End_Minute"></span>分（公休日，节假日除外）到\r\n\t\t\t\t\t\t\t\t\t\t<u>\r\n                                            \r\n                                        </u> 报名，报名经办人须携带本人身份证件，并于\r\n\t\t\t\t\t\t\t\t\t\t<span id="ApplyStartDate"></span>\r\n                                    <span id="SQSW_Start_Hour"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQSW_Start_Minute"></span>分，至\r\n\t\t\t\t\t\t\t\t\t\t<span id="ApplyEndDate"></span>\r\n                                    <span id="SQXW_End_Hour"></span>时\r\n\t\t\t\t\t\t\t\t\t\t<span id="SQXW_End_Minute"></span>分（公休日、节假日除外）到\r\n\t\t\t\t\t\t\t\t\t\t<u>\r\n                                            \r\n                                        </u>提交资格预审文件。</td>\r\n</tr>\r\n\r\n                            <tr id="Attach">\r\n\t<td align="center" bgcolor="#e5f2fa">相关附件</td>\r\n\t<td valign="top" colspan="3">\r\n                                    <br>\r\n                                    <table id="dlstAttachFile" cellspacing="0" border="0" style="width:100%;border-collapse:collapse;">\r\n\t\t<tr>\r\n\t\t\t<td>\r\n                                        </td>\r\n\t\t</tr><tr>\r\n\t\t\t<td>\r\n                                            <a href="http://www.jszb.com.cn/JSZB/ReadAttachFile.aspx?AttachID=bf64ed58-21c1-4855-b5cd-219178679f65" target="_blank"><font color="blue">\r\n                                                    定稿招标文件----徐州经济技术开发区珑越东方配套市政道路工程(1)_20230215093810.pdf\r\n                                                </font></a>\r\n                                        </td>\r\n\t\t</tr>\r\n\t</table>\r\n                                </td>\r\n</tr>\r\n\r\n                            \r\n                        </table>',
        'url': 'http://www.jszb.com.cn/jszb/YW_info/ZhaoBiaoGG/ViewReportDetail.aspx?RowID=827246',
        'source_name': '江苏省建设工程招标网',
        'other': '',
        'filepath': 'other_test/6831ce0c8e721da4febe98439cb6765e.html'
    }
    tran = Translate(data)
    # tran.check()
    tran.run()
