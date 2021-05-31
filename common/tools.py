import time
import json
import random


# 时间转换
def time_exchange(timeStamp):
    """
    时间戳转换为日期
    :param timeStamp:
    :return:
    """
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


# 针对字典提取错误
def safe_get(data, *args):
    """
    用于对多层字典取值
    :param data: 字典类型
    :param args: 从外层依次向里层的参数
    :return:
    """
    assert isinstance(data, dict), "data必须为字典"
    result = None
    for arg in args:
        result = data.get(arg)
        if result:
            data = result
    return result


def random_sleep(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))


if __name__ == '__main__':
    # data1 = {
    #     'a': 1,
    #     'b': {
    #         'c': 2,
    #         'd': {
    #             'e': 3
    #         },
    #
    #     }
    # }
    # data2 = []
    #
    # res = safe_get(data2,'b','d','e')
    # print(res)

    print(random.uniform(1, 5))
