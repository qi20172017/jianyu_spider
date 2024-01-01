

from celery import Celery
from kombu import Exchange, Queue, binding


moen_exchange = Exchange('moen', type='topic')


def moen_route_task(name, args, kwargs, options, task=None, **kw):
    exchange = options.get('exchange', 'moen')
    exchange_type = options.get('exchange_type', 'topic')
    routing_key = options.get('routing_key', name)
    return {
        'exchange': exchange,
        'exchange_type': exchange_type,
        'routing_key': routing_key
    }


moen_queues = [
    Queue(
        'bid.jianyu.zl_search',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.zl_search')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.zl_search_keyword',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.zl_search_keyword')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.search',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.search')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.search_keyword',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.search_keyword')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.detail',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.detail')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.clean',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.clean')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.zoo',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.zoo')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'bid.jianyu.kfk',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.kfk')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.captor_cookies',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.captor_cookies')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.require',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.require')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.history_tmp',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.history_tmp')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'bid.jianyu.require.detail',
        [binding(exchange=moen_exchange, routing_key='bid.jianyu.require.detail')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'bid.zhiliao.search',
        [binding(exchange=moen_exchange, routing_key='bid.zhiliao.search')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'bid.zhiliao.detail',
        [binding(exchange=moen_exchange, routing_key='bid.zhiliao.detail')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'bid.zhiliao.clean',
        [binding(exchange=moen_exchange, routing_key='bid.zhiliao.clean')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
]


# http://127.0.0.1:15672/#/queues  mq地址

MOEN = {
    # 'broker_url': 'amqp://guest:guest@127.0.0.1:5672/',
    'broker_url': 'amqp://guest:123456@106.75.36.245:5672/',
    # 默认任务配置
    'task_create_missing_queues': True,
    'task_default_delivery_mode': 'persistent',
    "worker_prefetch_multiplier": 4,
    'task_acks_late': True,
    'task_reject_on_worker_lost': True,
    'task_acks_on_failure_or_timeout': False,
    # 'task_track_started': True,
    'timezone': "Asia/Shanghai",
    # 发送端路由
    'task_queues': moen_queues,
    'task_routes': (moen_route_task,),
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


moenApp = Celery()
moenApp.config_from_object(MOEN)
