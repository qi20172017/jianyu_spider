#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : test_file.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/2/20 下午2:00
@Desc  :
/root/other_bid_project/ToolOfAnalysls/venv/bin/python /root/other_bid_project/ToolOfAnalysls/server/script/U_infomation.py >> /data/bid_project_logs/U.log



[program:bid] ;项目名称
command = /root/anaconda3/bin/python /opt/bid_ucloud_saves.py ; 启动命令
process_name=%(program_name)s_%(process_num)02d
numprocs = 1         ; 开启的进程数量
autostart = true     ; 在 supervisord 启动的时候也自动启>动
startsecs = 5        ; 启动 5 秒后没有异常退出，就当作已>经正常启动了
autorestart = false   ; 程序异常退出后自动重启
startretries = 3     ; 启动失败自动重试次数，默认是 3
user = root          ; 用哪个用户启动
# 把stderr重定向到stdout，默认false;
redirect_stderr = true
# 标准日志输出;
stdout_logfile=/data/logs/bid.log
# 错误日志输出;
stderr_logfile=/data/logs/err-bid.log
# 标准日志文件大小，默认50MB;
stdout_logfile_maxbytes = 20MB
# 标准日志文件备份数;
stdout_logfile_backups = 20



"""
import time

def print_hello():
    while True:
        print(f'{time.time()}: hello')
        time.sleep(1)


if __name__ == '__main__':
    print_hello()