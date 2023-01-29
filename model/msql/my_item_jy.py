#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : my_item_csdn.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2022/2/9 下午7:31
@Desc  : 
"""

from sqlalchemy import Column, String, Integer, BigInteger, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
import datetime
from model.msql.my_moen_db import MyBase, MySESSION
from model.mixin import ModelMixin


class JY(MyBase, ModelMixin):
    __tablename__ = "other_bid_info"

    __key__ = 'uuid'
    __table_args__ = (
        {"schema": "spider"}
    )

    session = MySESSION

    id = Column(BigInteger, primary_key=True, comment='')
    uuid = Column(BigInteger, nullable=False)
    title = Column(String, nullable=False)
    notice_type = Column(Integer, nullable=True, default=1)

    bid_type = Column(String, nullable=True, default='')
    bidding_type = Column(String, default='')
    invite_company = Column(String, nullable=True, default='')
    win_company = Column(String, nullable=True, default='')
    agency_company = Column(String, nullable=True, default='')
    pub_province = Column(String, nullable=True, default='')
    pub_city = Column(String, nullable=True, default='')
    pub_district = Column(String, nullable=True, default='')
    pub_addr = Column(String, nullable=True, default='')
    pub_time = Column(String, nullable=False, default='')

    tender_time = Column(TIMESTAMP(precision=0), nullable=True, default='1971-01-01 00:00:00', comment='作品创建时间')
    item_number = Column(String, default='')
    products = Column(String, nullable=True, default='')
    money = Column(String, nullable=True, default='')
    unit = Column(String, nullable=True, default='元')
    notice_detail = Column(Text, nullable=True, default='')

    url = Column(String, nullable=True, default='')
    filepath = Column(String, nullable=True, default='')
    doc = Column(String, nullable=True, default='')


    create_time = Column(TIMESTAMP(precision=0), nullable=False, default=datetime.datetime.now, comment='记录创建时间')

    update_time = Column(
        TIMESTAMP(precision=0),
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment='记录更新时间',
        index=True
    )

    source_name = Column(String, nullable=False, default='')
    other = Column(String, nullable=False, default='')


class JY_TEST(MyBase, ModelMixin):
    __tablename__ = "other_bid_info_test"

    __key__ = 'uuid'
    __table_args__ = (
        {"schema": "spider"}
    )

    session = MySESSION

    id = Column(BigInteger, primary_key=True, comment='')
    uuid = Column(BigInteger, nullable=False)
    title = Column(String, nullable=False)
    notice_type = Column(Integer, nullable=True, default=1)

    bid_type = Column(String, nullable=True, default='')
    bidding_type = Column(String, default='')
    invite_company = Column(String, nullable=True, default='')
    win_company = Column(String, nullable=True, default='')
    agency_company = Column(String, nullable=True, default='')
    pub_province = Column(String, nullable=True, default='')
    pub_city = Column(String, nullable=True, default='')
    pub_district = Column(String, nullable=True, default='')
    pub_addr = Column(String, nullable=True, default='')
    pub_time = Column(String, nullable=False, default='')

    tender_time = Column(TIMESTAMP(precision=0), nullable=True, default='1971-01-01 00:00:00', comment='作品创建时间')
    item_number = Column(String, default='')
    products = Column(String, nullable=True, default='')
    money = Column(String, nullable=True, default='')
    unit = Column(String, nullable=True, default='元')
    notice_detail = Column(Text, nullable=True, default='')

    url = Column(String, nullable=True, default='')
    filepath = Column(String, nullable=True, default='')
    doc = Column(String, nullable=True, default='')


    create_time = Column(TIMESTAMP(precision=0), nullable=False, default=datetime.datetime.now, comment='记录创建时间')

    update_time = Column(
        TIMESTAMP(precision=0),
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment='记录更新时间',
        index=True
    )

    source_name = Column(String, nullable=False, default='')
    other = Column(String, nullable=False, default='')

if __name__ == '__main__':
    pass