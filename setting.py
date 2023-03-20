import os

# 项目根路径
BASE_DIR = os.path.dirname(__file__)

local = True

if local:
    REDISDB_IP_PORTS = "106.75.108.206:6380"
    REDISDB_USER_PASS = "tianzhuanjiawa_009"

else:
    REDISDB_IP_PORTS = "10.9.186.118:6379"
    REDISDB_USER_PASS = "tianzhuanjiawa_009"

REDISDB_DB = 3

proxies = {'http': 'http://H6096HR7D67E18LD:E9E98060AB803CC0@http-dyn.abuyun.com:9020',
            'https': 'http://H6096HR7D67E18LD:E9E98060AB803CC0@http-dyn.abuyun.com:9020'}
