# -*- coding: utf-8 -*-
from sqlalchemy.exc import IntegrityError

from exceptions.exception import TuNotExistsException
from model.pg.pg_item_tu8tu import PgTu8tu
from model.serialize import serialize


class PgTuDao(object):

    @classmethod
    def get(cls, room_id):
        """
        通过用户唯一id， 获取用户的基础数据
        :param uid:
        :return:
        """
        room = PgTu8tu.get(room_id)
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
            PgTu8tu.add(**room)
            return flag
        except IntegrityError:
            flag = False
            return flag

    @classmethod
    def update(cls, room_id, **kwargs):
        PgTu8tu.update(room_id, **kwargs)

    @classmethod
    def upsert(cls, item_id, **kwargs):
        flag = PgTu8tu.upsert(item_id, **kwargs)
        return flag

    @classmethod
    def mark_live_status(cls, room_id, **kwargs):
        PgTu8tu.mark_live_status(room_id, **kwargs)