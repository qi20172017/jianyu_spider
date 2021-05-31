# -*- coding: utf-8 -*-
import hashlib, arrow, random

# 62进制字典
str62keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
             "a", "b", "c", "d", "e", "f", "g", "h", "i",
             "j", "k", "l", "m", "n", "o", "p", "q",
             "r", "s", "t", "u", "v", "w", "x", "y",
             "z", "A", "B", "C", "D", "E", "F", "G", "H",
             "I", "J", "K", "L", "M", "N", "O", "P",
             "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]


def md5(string):
    """ md5 hex-digest

    :param string: input string
    :return: hex-digested md5 string
    """
    return hashlib.md5(string).hexdigest()


def int10to62(int10):
    """
    10进制值转换为62进制

    >>> int10to62(0)
    '0'

    >>> int10to62(1)
    '1'

    >>> int10to62(61)
    'Z'
    """
    s62 = ''
    r = 0
    while int10 != 0:
        int10, r = divmod(int10, 62)
        s62 += str62keys[r]
    if not s62:
        s62 = '0'
    return s62[::-1]


def str62to10(str62):
    """
    62进制值转换为10进制

    >>> str62to10('0')
    0

    >>> str62to10('1')
    1

    >>> str62to10('Z')
    61
    """
    res = 0
    for i in str62:
        res = res * 62 + str62keys.index(i)
    return res


def mid2url(mid):
    """
    将微博 mid 转化为 URL 中的占位符, 如果 mid 以 0 开头需要传入字符串

    >>> mid2url(4079837322916098)
    'ExuVSceBQ'

    >>> mid2url(4076482110338253)
    'Ew5Ef1pZH'

    >>> mid2url('0000000000000000')
    '000000000'
    """
    mid = str(mid)
    url = ''
    for i in range(len(mid), 0, -7):
        piece = mid[i - 7 if i > 7 else 0: i]
        piece = int10to62(int(piece))
        if i > 7:
            url = '{:0>4}{}'.format(piece, url)
        else:
            url = '{:0>1}{}'.format(piece, url)
    return url


def url2mid(url):
    """
    将 URL 中的占位符转化为微博 mid

    >>> url2mid('ExuVSceBQ')
    4079837322916098

    >>> url2mid('EqsMxni5h')
    4063071695551063

    >>> url2mid('Ew5Ef1pZH')
    4076482110338253
    """
    mid = ''
    for i in range(len(url), 0, -4):
        num = url[i - 4 if i > 4 else 0: i]
        num = str62to10(num)
        mid = '{:0>7}{}'.format(num, mid)
    return int(mid)


def get_weibo_url(uid, mid):
    """
    返回单条微博链接地址
    """
    return 'http://www.weibo.com/{0}/{1}'.format(uid, mid2url(mid))


def get_toutiao_article_url(item_id):
    return 'http://www.toutiao.com/item/{}'.format(item_id)


# def build_cyphertext(plaintext, salt='valid_for_callback'):
#     """
#     md5 加盐加密
#     :param plaintext:
#     :param salt:
#     :return:
#     """
#     if type(plaintext) == unicode:
#         plaintext = plaintext.encode('utf-8')
#     return md5(plaintext+salt)


def build_toutiao_token(tth_id):
    salt = "toutiao_mp_open_data"
    return md5(tth_id+salt)


def generate_id():
    """
    gennerate reserve id for monitoring mp, weibo, toutiao article
    :return:
    """
    project_id = arrow.now().format("YYSSDDhhmmssMM") + \
                 "%02i" % (random.random() * 100)
    return mid2url(project_id)


if __name__ == '__main__':
    mid = url2mid('HsPTokNPw')
    print(mid)
    # url = mid2url('4359606051846394')
    # print(url)