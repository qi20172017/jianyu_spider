#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : ctbpsp.py
@Author: crawlSpider
@Address: https://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%BD%91%E8%99%ABspider&ie=utf8&_sug_=n&_sug_type_=
@Github: https://github.com/qi20172017
@Date  : 2023/7/28 下午4:01
@Desc  : 
"""
import time

import requests
from Crypto.Cipher import AES, DES
import base64
from model.rds import rds_206_11
from plantform.jianyu import get_proxy_ip

class prpcrypt():
    def __init__(self):
        # key值（密码）
        # 因为在python3中AES传入参数的参数类型存在问题，需要更换为 bytearray , 所以使用encode编码格式将其转为字节格式（linux系统可不用指定编码）
        self.key = 'v4dj1g1lfekof8sz'.encode("utf-8")
        # vi偏移量
        self.iv = 'hs2s8eop6pn6cf89'.encode("utf-8")  # 编码
        self.mode = AES.MODE_CBC
        self.BS = AES.block_size
        self.pad = lambda s: s + (self.BS - len(s) %
                                  self.BS) * chr(self.BS - len(s) % self.BS)
        self.unpad = lambda s: s[0:-ord(s[-1])]

    # 加密
    def encrypt(self, text):
        text = self.pad(text).encode("utf-8")
        cryptor = AES.new(self.key, self.mode, self.iv)
        # 目前AES-128 足够目前使用(CBC加密)
        ciphertext = cryptor.encrypt(text)
        # base64加密
        return base64.b64encode(bytes(ciphertext))

    # 解密
    def decrypt(self, text):
        # base64解密
        text = base64.b64decode(text)
        cryptor = AES.new(self.key, self.mode, self.iv)
        # CBC解密
        plain_text = cryptor.decrypt(text)
        # 去掉补足的空格用strip() 去掉
        return self.unpad(bytes.decode(plain_text).rstrip('\0'))  # 解密字节？？？


def des_decrypt(data, key):
    key = key.encode()
    data = base64.b64decode(data)  # b64decode传入参数可以是str，返回的是byte，所以这里执行后，data也是byte了
    des = DES.new(key, DES.MODE_ECB)
    data = des.decrypt(data)  # 解密得到的是明文经填充了的结果，byte类型
    result = unpadding(data)  # 去掉填充，str类型
    return result

def unpadding(data_e): #参数data_e是byte形式的、已经填充的data
    data_e=data_e[:-data_e[-1]] #去掉填充，这里直接去掉data_e的最后一位的值对应的长度，因为之前填充的填充位就是填充长度的数字（读起来太绕的话建议直接执行一下试试看效果，但要注意这里是【byte类型】才可以实现这种操作！）
    return data_e.decode() #byte转str


# from pyDes import des, CBC, PAD_PKCS5, ECB, PAD_PKCS7
# class USE_DES:
#     """
#     des (key, [mode], [IV], [pad], [pad mode])
# key-必须正好8字节
# mode（模式）：ECB、CBC
# iv:cBC模式中必须提供长8字节
# pad :填充字符
# eadmede ：加密填充模式PAD_ NORYAL or PAD_ PKCS5
#
#     """
#
#     def __init__(self, key, iv=''):
#         if not isinstance (key, bytes):
#             key = bytes(key, encoding="utf8")
#         if not isinstance(iv, bytes):
#             iv = bytes(iv, encoding="utf8")
#         self.key = key
#         self.iv = iv
#     def encrypt (self, text) :
#         """
#         DES TIE
#     Daram text：原始字符串
#     return：加密后字符串，bytes
#         :param self:
#         :param text:
#         :return:
#         """
#
#         if not isinstance (text, bytes):
#             text = bytes (text,"utf-8")
#         secret_key = self.key
#         iv = self.iv
#         k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
#         en = k.encrypt (text, padmode=PAD_PKCS5)
#         return en
#     def descrypt (self, text):
#         """
#             DES 解密
#     sparam text：加密后的字符串，bytesreturn：解密后的字符串
#         :param text:
#         :return:
#         """
#
#         secret_key = self.key
#         # iv = self.iv
#         k = des(secret_key, ECB, pad=None, padmode=PAD_PKCS5)
#         de = k.decrypt(text, padmode=PAD_PKCS5)
#         return de.decode()



def get_list():

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'http://ctbpsp.com',
        'Pragma': 'no-cache',
        'Referer': 'http://ctbpsp.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    response = requests.get('https://ctbpsp.com/cutominfoapi/recommand/type/5/pagesize/10/currentpage/3',
                            proxies = get_proxy_ip(''),
                            headers=headers)

    print(response.text)

    res = decode(response.text[1:-1])

    print(res.text)
    # dd = USE_DES('1qaz@wsx3e')
    # res = dd.descrypt(response.text)
    # res = des_decrypt(response.text, '1qaz@wsx3e')
    # print(res)
    data = res.json()['data']['dataList']
    for item in data:
        bulletinID = item['bulletinID']
        tenderProjectName = item['tenderProjectName']
        print(tenderProjectName, bulletinID)
        try:
            pdf_url(bulletinID)
        except Exception as e:
            print(e)
        time.sleep(2)

def decode(data):
    body = {
        'data': data
    }

    res = requests.post('http://172.20.1.252:8090/get_ctb_decode', body)

    return res

def pdf_url(item_id):

    cookies = {
        'route': '2d537f5baec9369210a4429f0163a741',
        'Hm_lvt_b966fe201514832da03dcf6cbf25b8a2': '1690770771',
        'BSFIT_EXPIRATION': '1690832221723',
        'BSFIT_DEVICEID': 'WkdkSoBbva_t1-mfrA-6zdTukpju4y6e3s8qVH3x6Rv_VCcM0Z5K8mO-DH9J4A1LFn4c9PE67LQwnoyoSFMi9PYXHZicnaP9xRViL2Ee61QBCkprBnGc5CMR331v_UfHCWko9K9hjNHR1lxUwiOrodIc3zVdJ1_m',
        'BSFIT_t4sym': '',
        '__ts': '1690771184003',
        'Hm_lpvt_b966fe201514832da03dcf6cbf25b8a2': '1690771197',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'route=2d537f5baec9369210a4429f0163a741; Hm_lvt_b966fe201514832da03dcf6cbf25b8a2=1690770771; BSFIT_EXPIRATION=1690832221723; BSFIT_DEVICEID=WkdkSoBbva_t1-mfrA-6zdTukpju4y6e3s8qVH3x6Rv_VCcM0Z5K8mO-DH9J4A1LFn4c9PE67LQwnoyoSFMi9PYXHZicnaP9xRViL2Ee61QBCkprBnGc5CMR331v_UfHCWko9K9hjNHR1lxUwiOrodIc3zVdJ1_m; BSFIT_t4sym=; __ts=1690771184003; Hm_lpvt_b966fe201514832da03dcf6cbf25b8a2=1690771197',
        'Pragma': 'no-cache',
        'Referer': 'https://ctbpsp.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    response = requests.get(
        f'https://ctbpsp.com/cutominfoapi/bulletin/{item_id}/uid/0',
        proxies=get_proxy_ip(''),
        # cookies=cookies,
        headers=headers,
    )

    print(response.text)

    res = decode(response.text[1:-1])
    data = res.json()['data']
    pdfUrl = data['pdfUrl']
    print(pdfUrl)
    pdf(pdfUrl)

def pdf(url):


    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'route=2d537f5baec9369210a4429f0163a741; Hm_lvt_b966fe201514832da03dcf6cbf25b8a2=1690770771; BSFIT_EXPIRATION=1690832221723; BSFIT_DEVICEID=WkdkSoBbva_t1-mfrA-6zdTukpju4y6e3s8qVH3x6Rv_VCcM0Z5K8mO-DH9J4A1LFn4c9PE67LQwnoyoSFMi9PYXHZicnaP9xRViL2Ee61QBCkprBnGc5CMR331v_UfHCWko9K9hjNHR1lxUwiOrodIc3zVdJ1_m; BSFIT_t4sym=; Hm_lpvt_b966fe201514832da03dcf6cbf25b8a2=1690772331; __ts=1690772334003',
        'Pragma': 'no-cache',
        'Referer': 'https://ctbpsp.com/web_pdf/pdfjs-dist/web/viewer.html?file=https://ctbpsp.com/cutominfoapi/bulletinPDF/b3850b010aa44672874b1cc2ef961359',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    response = requests.get(
        url,
        headers=headers,
    )
    file_name = url.split('PDF/')[1]
    print(response.content)
    with open(f'./{file_name}.pdf', 'wb') as f:
        f.write(response.content)


def detail():

    cookies = {
        'route': 'ef535e3a0d0b78922cdc0df3d6b94403',
        'Hm_lvt_b966fe201514832da03dcf6cbf25b8a2': '1690530696',
        'BSFIT_EXPIRATION': '1690592944793',
        'BSFIT_DEVICEID': 'gPAcIb4zP922AJMFfdmQnNyOeqYlpxKeFnQAyWnsu-GgdAZGTbsFjyYjUvS2aR1XNJhLTi__q_HPe93LQcCEEp0j3MR82xNq3_Y9xJKmbmKQlm0QODEFIXOyq2L10v22rz98VPAeb1aMtzniym3Gyk7P_1YN0lXx',
        'BSFIT_h1q0+': '',
        '__ts': '1690535417005',
        'Hm_lpvt_b966fe201514832da03dcf6cbf25b8a2': '1690535657',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'route=ef535e3a0d0b78922cdc0df3d6b94403; Hm_lvt_b966fe201514832da03dcf6cbf25b8a2=1690530696; BSFIT_EXPIRATION=1690592944793; BSFIT_DEVICEID=gPAcIb4zP922AJMFfdmQnNyOeqYlpxKeFnQAyWnsu-GgdAZGTbsFjyYjUvS2aR1XNJhLTi__q_HPe93LQcCEEp0j3MR82xNq3_Y9xJKmbmKQlm0QODEFIXOyq2L10v22rz98VPAeb1aMtzniym3Gyk7P_1YN0lXx; BSFIT_h1q0+=; __ts=1690535417005; Hm_lpvt_b966fe201514832da03dcf6cbf25b8a2=1690535657',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    response = requests.get('https://ctbpsp.com/',
                            # cookies=cookies,
                            verify=False,
                            headers=headers)
    print(response.content.decode())
if __name__ == '__main__':
    get_list()
    # detail()

    # data = "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"
    #
    # for i in range(100):
    #     res = decode(data)
    #     print(i, res.text)
