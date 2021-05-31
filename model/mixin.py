# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import text
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
import datetime
import json
from functools import partial


class ModelMixin(object):
    __key__ = None
    __table_args__ = None
    __tablename__ = None

    @classmethod
    @contextmanager
    def session_context(cls, autocommit=False):
        session = cls.session()
        try:
            yield session
            if autocommit:
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            cls.session.remove()

    @classmethod
    def get(cls, key):
        with cls.session_context() as session:
            record = session.query(cls).filter(getattr(cls, cls.__key__) == key).first()
            if record:
                return record

    @classmethod
    def gets(cls, key):
        with cls.session_context() as session:
            records = session.query(cls).filter_by(getattr(cls, cls.__key__) == key).all()
            if records:
                return records

    @classmethod
    def execute_gen(cls, sql, type='select', **kwargs):
        def scan(query):
            for row in query.fetchall():
                yield dict(zip(row._parent.keys, row._row))

        with cls.session_context(autocommit=True) as session:
            data = {}
            result = session.execute(
                sql.replace(
                    ':t_name', cls.__table_args__['schema'] + '.' + cls.__tablename__
                ).replace(':key_field', cls.__key__), kwargs
            )

            if type.lower() == 'select':
                data['rows'] = scan(result)
            data['rowcount'] = result.rowcount
        return data

    @classmethod
    def execute(cls, sql, type='select', **kwargs):
        with cls.session_context(autocommit=True) as session:
            data = {}
            result = session.execute(sql, kwargs)

            if type.lower() == 'select':
                data['rows'] = [dict(zip(row._parent.keys, row._row)) for row in result.fetchall()]
            data['rowcount'] = result.rowcount
        return data

    @classmethod
    def add(cls, **kwargs):
        obj = cls(**kwargs)
        with cls.session_context(autocommit=True) as session:
            session.add(obj)

    @classmethod
    def add_all(cls, objs):
        result = []
        for i, obj in enumerate(objs):
            try:
                with cls.session_context(autocommit=True) as session:
                    session.add(cls(**obj))
            except IntegrityError as e:
                result.append((i, e))
        return result

    @classmethod
    def update(cls, _id, **kwargs):
        with cls.session_context(autocommit=True) as session:
            session.query(cls).filter(getattr(cls, cls.__key__) == _id).update(kwargs)

    @classmethod
    def upsert(cls, _id, json_mode=None, **kwargs):
        """
        - ``json_mode``: 1
        """
        with cls.session_context(autocommit=True) as session:

            records = session.query(cls).with_for_update().filter(getattr(cls, cls.__key__) == _id)
            record = records.first()
            if record:
                kwargs['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for k, v in kwargs.items():
                    if json_mode == 1:
                        setattr(record, k, v)
                    else:
                        record_col = getattr(record, k)
                        if isinstance(record_col, dict):
                            record_col.update({k: v})
                            setattr(record, k, record_col)
                        elif isinstance(record_col, list):
                            record_col.extend(v)
                            setattr(record, k, list(set(record_col)))
                        else:
                            setattr(record, k, v)
                return False
            else:
                kwargs[cls.__key__] = _id
                session.add(cls(**kwargs))
                return True

    @classmethod
    def bulk_upsert(cls, objs):
        with cls.session_context(autocommit=True) as session:
            for obj in objs:
                records = session.query(cls).with_for_update().filter(getattr(cls, cls.__key__) == obj[cls.__key__])
                record = records.first()
                if record:
                    obj['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    for k, v in obj.items():
                        record_col = getattr(record, k)
                        if isinstance(record_col, dict):
                            record_col.update({k: v})
                            setattr(record, k, record_col)
                        elif isinstance(record_col, list):
                            record_col.extend(v)
                            setattr(record, k, list(set(record_col)))
                        else:
                            setattr(record, k, v)
                else:
                    session.add(cls(**obj))

    @classmethod
    def add_with_conflict(cls, **kwargs):
        with cls.session_context(autocommit=True) as session:
            kwargs['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            session.execute(Insert(cls).values(**kwargs).on_conflict_do_update(
                index_elements=[cls.__key__],
                set_=kwargs
            ))

    @classmethod
    def add_all_with_conflict(cls, objs):
        with cls.session_context(autocommit=True) as session:
            for obj in objs:
                obj['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                session.execute(Insert(cls).values(**obj).on_conflict_do_update(
                    index_elements=[cls.__key__],
                    set_=obj
                ))

    @classmethod
    def add_all_with_conflict_do_nothing(cls, objs):
        with cls.session_context(autocommit=True) as session:
            for obj in objs:
                session.execute(Insert(cls).values(**obj).on_conflict_do_nothing(
                    index_elements=[cls.__key__],
                ))

    @classmethod
    def add_with_conflict_do_nothing(cls, **kwargs):
        with cls.session_context(autocommit=True) as session:
            session.execute(Insert(cls).values(**kwargs).on_conflict_do_nothing(
                index_elements=[cls.__key__],
            ))

    @classmethod
    def search(cls, **kwargs):
        with cls.session_context() as session:
            filter_ = []
            for k, v in kwargs.items():
                filter_.append(getattr(cls, k) == v)

            record = session.query(cls).filter(*filter_).all()
            if record:
                return record
            else:
                return None


def _serialize(obj, props=None, exclude=None):
    if isinstance(obj, dict):
        return obj
    names = set(obj._sa_class_manager.local_attrs.keys()).union(props or [])
    if exclude is not None:
        names = names - exclude

    return {name: getattr(obj, name) for name in names}


def serialize(obj, props=None, exclude=None):
    """
    Serialize SQLAlchemy model.

    :param obj: SQLAlchemy model object.
    :return: dict object
    """
    if exclude is None:
        exclude = set()

    if isinstance(obj, list):
        return list(map(partial(_serialize, props=props, exclude=set(exclude)), obj))
    return _serialize(obj, props, exclude)