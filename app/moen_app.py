import copy
import time

from celery import Task, Celery
from kombu import Exchange, Queue, binding

# from common.exception import CritError
# from duck.service.kuaishou.kuaishou import logger
# from setting import config

# kwai_data_exchange = Exchange('kuaishou.data', type='topic')
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
        'moen.tu8tu.list',
        [binding(exchange=moen_exchange, routing_key='moen.tu8tu.list')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'moen.tu8tu.picture',
        [binding(exchange=moen_exchange, routing_key='moen.tu8tu.picture')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'moen.tu8tu.article',
        [binding(exchange=moen_exchange, routing_key='moen.tu8tu.article')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'moen.tu8tu.diary',
        [binding(exchange=moen_exchange, routing_key='moen.tu8tu.diary')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'moen.tu8tu.question',
        [binding(exchange=moen_exchange, routing_key='moen.tu8tu.question')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

    Queue(
        'moen.haozu.list',
        [binding(exchange=moen_exchange, routing_key='moen.haozu.list')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'moen.haozu.house',
        [binding(exchange=moen_exchange, routing_key='moen.haozu.house')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),
    Queue(
        'moen.haozu.article',
        [binding(exchange=moen_exchange, routing_key='moen.haozu.article')],
        queue_arguments={'x-queue-mode': 'lazy'}
    ),

]

MOEN = {
    # 'broker_url': 'amqp://guest:guest@127.0.0.1:5672/',
    'broker_url': 'amqp://mquser:123456@10.0.4.104:5672/moen',
    # 默认任务配置
    'task_create_missing_queues': True,
    'task_default_delivery_mode': 'persistent',
    "worker_prefetch_multiplier": 4,
    # 'task_track_started': True,
    'timezone': "Asia/Shanghai",
    # 发送端路由
    'task_queues': moen_queues,
    'task_routes': (moen_route_task,),
    # 日志
    'worker_task_log_format': "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    'worker_log_format': "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
}


# class BaseTask(Task):
#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         logger.error('[%s]: error: %s-%s, args:[%s], kwargs:[%s]' % (exc, self.name, task_id, args, kwargs))
#         if isinstance(exc, CritError):
#             return
#         elif str(exc).__contains__('操作太快'):  # 此为video detail ip限制(访问速率)
#             return
#         elif str(exc).__contains__('cookie无效'):  # 此为comment update ip限制(访问成功率)
#             return
#
#         kwargs['exc'] = str(exc)
#         kwargs['einfo'] = str(einfo)
#         signature = self.signature_from_request(
#             self.request, args, kwargs,
#             countdown=0,
#             eta=None,
#             queue='kwai.failed',
#         )
#         signature.apply_async()
#
#     def on_retry(self, exc, task_id, args, kwargs, einfo):
#         # if not str(exc).__contains__('操作太快') and not str(exc).__contains__('cookie无效'):
#         #     logger.warning('[%s]:retry: %s-%s,  args:[%s], kwargs:[%s]' % (exc, self.name, task_id, args, kwargs))
#         logger.warning('[%s]:retry: %s-%s,  args:[%s], kwargs:[%s]' % (exc, self.name, task_id, args, kwargs))
#
#     def on_success(self, retval, task_id, args, kwargs):
#         if self.name in ('kwai.spider.cookie.heartbeat', 'kwai.spider.cookie.activate'):
#             return
#         logger.info('%s-[%s]:success, args:[%s], kwargs:[%s]' % (self.name, task_id, args, kwargs))


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
