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

from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import TIMESTAMP
import datetime
from model.msql.my_moen_db import MyBase, MySESSION
from model.mixin import ModelMixin


class CSDN(MyBase, ModelMixin):
    __tablename__ = "CSDN"

    __key__ = 'item_id'
    __table_args__ = (
        {"schema": "moen"}
    )

    session = MySESSION

    item_id = Column(String, primary_key=True, comment='')
    create_time = Column(TIMESTAMP(precision=0), nullable=True, comment='作品创建时间')

    insert_time = Column(TIMESTAMP(precision=0), nullable=False, default=datetime.datetime.now, comment='记录创建时间')

    update_time = Column(
        TIMESTAMP(precision=0),
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment='记录更新时间',
        index=True
    )
    article_id = Column(Integer, nullable=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)
    article_type = Column(String, nullable=True, comment='文章类型 1原创 2转载')
    top = Column(String, nullable=True, comment='是否置顶')

    author = Column(String, nullable=True)

    view_count = Column(Integer, nullable=True, comment='观看数')
    like_count = Column(Integer, nullable=True, comment='喜欢、点赞数')
    comment_count = Column(Integer, nullable=True, comment='评论数')

    platform = Column(String, nullable=True, comment='平台')

if __name__ == '__main__':
    pass