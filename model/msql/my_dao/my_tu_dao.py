# -*- coding: utf-8 -*-
from sqlalchemy.exc import IntegrityError

from exceptions.exception import TuNotExistsException
from model.msql.my_item_tu8tu import Tu8tu
from model.serialize import serialize


class MyTuDao(object):

    @classmethod
    def get(cls, room_id):
        """
        通过用户唯一id， 获取用户的基础数据
        :param uid:
        :return:
        """
        room = Tu8tu.get(room_id)
        if room:
            return serialize(room)

        raise TuNotExistsException(room_id)

    @classmethod
    def add(cls, room):
        """
        插入一条用户记录
        :param room:
        :return:
        """
        flag = True
        try:
            Tu8tu.add(**room)
            return flag
        except IntegrityError:
            flag = False
            return flag

    @classmethod
    def update(cls, room_id, **kwargs):
        Tu8tu.update(room_id, **kwargs)

    @classmethod
    def upsert(cls, item_id, **kwargs):
        flag = Tu8tu.upsert(item_id, **kwargs)
        return flag

    @classmethod
    def mark_live_status(cls, room_id, **kwargs):
        Tu8tu.mark_live_status(room_id, **kwargs)