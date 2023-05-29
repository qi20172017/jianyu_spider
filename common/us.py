#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : us.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/5/15 下午3:19
@Desc  : 
"""
import os
import math
import re
import time
from io import BytesIO

from ufile import config,filemanager
test = False


def upload_us3(item):
    uuid = item['uuid']
    text = item['notice_detail']

    ufile = UfileOss()
    if test:
        folder_name = "other_test/"
    else:
        folder_name = "other_bid"

    for _ in range(6):
        try:
            file_name = f"{uuid}.html"
            result_file = os.path.join(folder_name, file_name)
            ufile.upload_bytesIO(result_file, text.encode('utf-8'), mime_type='text/html')

            return result_file
        except Exception as e:
            time.sleep(0.05)
    return None

class UfileOss(object):
    public_key = '4eXwD7vhEE5Ln9TGMvGARl30U9dau3Zq5'  # 账户公钥
    private_key = 'KK64s7lhLtrHx50cbD02cB1yli6DRguJwIHz2jpQ0x38'  # 账户私钥
    bucket = 'useful'  # 空间名称

    def __init__(self):
        self.ufile_handler = filemanager.FileManager(self.public_key, self.private_key)

    def upload_file(self, put_key,local_file):
        '''普通文件上传'''
        ret, resp = self.ufile_handler.putfile(self.bucket, put_key, local_file, header=None)
        assert resp.status_code == 200

    def upload_bytesIO(self, file, content,mime_type=None):
        '''二进制上传'''
        bio = BytesIO(content)
        ret, resp = self.ufile_handler.putstream(self.bucket, file, bio,mime_type=mime_type)
        assert resp.status_code == 200


if __name__ == '__main__':
    pass