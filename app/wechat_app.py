import copy
import time

from celery import Task, Celery
from kombu import Exchange, Queue, binding

# from common.exception import CritError
# from duck.service.kuaishou.kuaishou import logger
# from setting import config

# kwai_data_exchange = Exchange('kuaishou.data', type='topic')
wechat_exchange = Exchange('wechat', type='topic')


def wechat_route_task(name, args, kwargs, options, task=None, **kw):
    exchange = options.get('exchange', 'wechat')
    exchange_type = options.get('exchange_type', 'topic')
    routing_key = options.get('routing_key', name)
    return {
        'exchange': exchange,
        'exchange_type': exchange_type,
        'routing_key': routing_key
    }


wechat_queues = [
    Queue(
        'wechat.sougou.account',
        [binding(exchange=wechat_exchange, routing_key='wechat.sougou.account')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'wechat.sougou.content',
        [binding(exchange=wechat_exchange, routing_key='wechat.sougou.content')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'wechat.zoo',
        [binding(exchange=wechat_exchange, routing_key='wechat.zoo')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

]


# http://127.0.0.1:15672/#/queues  mq地址

WECHAT = {
    # 'broker_url': 'amqp://guest:guest@127.0.0.1:5672/',
    'broker_url': 'amqp://guest:123456@106.75.7.76:5672/',
    # 默认任务配置
    'task_create_missing_queues': True,
    'task_default_delivery_mode': 'persistent',
    "worker_prefetch_multiplier": 4,
    # 'task_track_started': True,
    'timezone': "Asia/Shanghai",
    # 发送端路由
    'task_queues': wechat_queues,
    'task_routes': (wechat_route_task,),
    # 日志
    'worker_task_log_format': "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    'worker_log_format': "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
}



def route_task_(ex_name, ex_type):
    def r_task(name, args, kwargs, options, task=None, **kw):
        return {
            'exchange': ex_name,
            'exchange_type': ex_type,
            'routing_key': name
        }

    return r_task


wechatApp = Celery()
wechatApp.config_from_object(WECHAT)
