#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : datang.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/7/31 下午2:01
@Desc  : 
"""
import re

import requests

from requests import session

class Datang:
    def __init__(self):
        self.session = session()
        self.cookie_v2 = ''

    def list(self):

        cookies = {
            # 'JSESSIONID': '6EB39E83C17030FEEF0E4D87BCBC6C5D',
            # 'acw_tc': '2760777516907829567748465e4725ad40352b30937e7dc5a7dcb4db9c8340',
            'acw_sc__v2': self.cookie_v2,
            # 'ssxmod_itna': 'YqGxc7DtitKQq0K40dD=G7IHB+DUoO7xf348RhBl4GXdwoGRDCqAPGfDI8fU3hf0DqebBhci58FW0Pr4UF/Cn4FcY=0ap3DvDAoDhx7QDo=qD12D09meTDeeDvDCeDIDWeDiDGbOnE2HF7DB4DjDBOfE5Dbxi3D4GCDmKDuE5DWcpwDDa8DWymBoywsxDCDGFmhx3DNr3=chv1uD0OrtTQK9SLnhHP4zxwjY5DX=ljEPuhqUHsfEjGQt2Da0RnTDWkKB+qH00FrWhnzB2dmliKrBG5aQG5eBwKH5Nx8zxxALhDD=',
            # 'ssxmod_itna2': 'YqGxc7DtitKQq0K40dD=G7IHB+DUoO7xf348RhD4A6cLheD/UYFfDFgRG/toOdKhk4HeqidHKIk0rCYu1g74pH+8n06vXttD4aL1VRcxaIKqdm92fWLjzfi5IPr165pIgoWKbRE6zxO8xAi8OIHqUFbVE7Fo6as+On4t4ckbRF8g6ApKgPwT+Obo8mTN891GtcO1z5EWbSvd1Wf1USE=oojN8PFmS3Uhb3CgB0rMzTrpFOanF92QkP2xzmsyW0r//7cBOIEgm=ue0=AR4gD61e+oEj9gQ/R8Rapq7IcGo/8Nu3AUylTGSzI2suh30Til3CE27dTd0qdxQ8mkFDjTCSsw37HWK4rYUE+vqTb418nGuTz1n+MM+wdpiS+r2p2WmQ3=WeIxrQUQN+QhMCPD7Q5WhPWmWmw3mI3AGkQn+tqNSqmSx3xxqQDy0I3YcdWxfzqbDGcDG7eiDD==',
        }

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'Cookie': 'JSESSIONID=6EB39E83C17030FEEF0E4D87BCBC6C5D; acw_tc=2760777516907829567748465e4725ad40352b30937e7dc5a7dcb4db9c8340; acw_sc__v2=64c74cee4d36a37c4dc29f83d9e430328ff5b09c; ssxmod_itna=YqGxc7DtitKQq0K40dD=G7IHB+DUoO7xf348RhBl4GXdwoGRDCqAPGfDI8fU3hf0DqebBhci58FW0Pr4UF/Cn4FcY=0ap3DvDAoDhx7QDo=qD12D09meTDeeDvDCeDIDWeDiDGbOnE2HF7DB4DjDBOfE5Dbxi3D4GCDmKDuE5DWcpwDDa8DWymBoywsxDCDGFmhx3DNr3=chv1uD0OrtTQK9SLnhHP4zxwjY5DX=ljEPuhqUHsfEjGQt2Da0RnTDWkKB+qH00FrWhnzB2dmliKrBG5aQG5eBwKH5Nx8zxxALhDD=; ssxmod_itna2=YqGxc7DtitKQq0K40dD=G7IHB+DUoO7xf348RhD4A6cLheD/UYFfDFgRG/toOdKhk4HeqidHKIk0rCYu1g74pH+8n06vXttD4aL1VRcxaIKqdm92fWLjzfi5IPr165pIgoWKbRE6zxO8xAi8OIHqUFbVE7Fo6as+On4t4ckbRF8g6ApKgPwT+Obo8mTN891GtcO1z5EWbSvd1Wf1USE=oojN8PFmS3Uhb3CgB0rMzTrpFOanF92QkP2xzmsyW0r//7cBOIEgm=ue0=AR4gD61e+oEj9gQ/R8Rapq7IcGo/8Nu3AUylTGSzI2suh30Til3CE27dTd0qdxQ8mkFDjTCSsw37HWK4rYUE+vqTb418nGuTz1n+MM+wdpiS+r2p2WmQ3=WeIxrQUQN+QhMCPD7Q5WhPWmWmw3mI3AGkQn+tqNSqmSx3xxqQDy0I3YcdWxfzqbDGcDG7eiDD==',
            'Origin': 'https://www.cdt-ec.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.cdt-ec.com/notice/moreController/toMore?globleType=0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        data = {
            'page': '2',
            'limit': '10',
            'messagetype': '0',
            'startDate': '',
            'endDate': '',
        }

        response = self.session.post('https://www.cdt-ec.com/notice/moreController/getList', cookies=cookies, headers=headers,
                                 data=data)
        print(response.text)
        arg1 = re.findall("arg1='(.*?)'", response.text)
        if arg1:
            self.arg1 = arg1[0]



    def get_cookie(self):

        res = requests.get(f'http://127.0.0.1:8090/get_acw_sc__v2?arg1={self.arg1}')
        print(res.text)
        self.cookie_v2 = res.text

    def run(self):

        self.list()
        self.get_cookie()
        self.list()

if __name__ == '__main__':
    # list()
    dt = Datang()

    # dt.get_cookie()
    # dt.list()
    dt.run()
