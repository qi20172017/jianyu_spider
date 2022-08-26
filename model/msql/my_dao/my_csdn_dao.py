#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : my_csdn_dao.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2022/2/10 上午11:02
@Desc  : 
"""
from sqlalchemy.exc import IntegrityError
from exceptions.exception import TuNotExistsException
from model.msql.my_item_csdn import CSDN
from model.serialize import serialize

class MyCsdnDao(object):
    @classmethod
    def update(cls, room_id, **kwargs):
        CSDN.update(room_id, **kwargs)

    @classmethod
    def upsert(cls, item_id, **kwargs):
        flag = CSDN.upsert(item_id, **kwargs)
        return flag


    @classmethod
    def get(cls, room_id):
        """
        通过用户唯一id， 获取用户的基础数据
        :param uid:
        :return:
        """
        room = CSDN.get(room_id)
        if room:
            return serialize(room)

        raise TuNotExistsException(room_id)





if __name__ == '__main__':
    pass