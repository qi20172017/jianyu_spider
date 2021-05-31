import datetime
import json
from functools import partial


def _serialize(obj, props=None):
    if isinstance(obj, dict):
        return obj

    names = set(obj._sa_class_manager.local_attrs.keys()).union(props or [])
    return {name: getattr(obj, name) for name in names}


def serialize(obj, props=None):
    """
    Serialize SQLAlchemy model.

    :param obj: SQLAlchemy model object.
    :return: dict object
    """
    if isinstance(obj, list):
        return map(partial(_serialize, props=props), obj)
    return _serialize(obj, props)


class DateTimeDecoder(json.JSONDecoder):

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()

        return super(DateTimeDecoder, self).default(obj)


def loads(s):
    return json.loads(s, cls=DateTimeDecoder)
