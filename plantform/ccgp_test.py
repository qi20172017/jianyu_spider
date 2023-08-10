import re
import requests
from lxml import etree
from bid_project_three.utils.tools import single_province, get_date
from bid_project_three.utils.ipool import Ipool
from bid_project_three.pipelines import Us3Pipeline, KafkaPipeline, MysqlPoolPipeline
# class Ccgp:
#     def __init__(self):
#         self.headers = {
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#             'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
#             'Cache-Control': 'no-cache',
#             'Connection': 'keep-alive',
#             'Pragma': 'no-cache',
#             'Referer': 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=2&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time=2023%3A07%3A28&end_time=2023%3A07%3A28&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName=',
#             'Upgrade-Insecure-Requests': '1',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
#         }

def get_page(start_time, headers):
    params = {
        'searchtype': '1',
        'page_index': '1',
        'bidSort': '0',
        'buyerName': '',
        'projectId': '',
        'pinMu': '0',
        'bidType': '0',
        'dbselect': 'bidx',
        'kw': '',
        'start_time': start_time,
        'end_time': start_time,
        'timeType': '6',
        'displayZone': '',
        'zoneId': '',
        'pppStatus': '0',
        'agentName': '',
    }
    try:
        response = requests.get('http://search.ccgp.gov.cn/bxsearch', params=params, headers=headers, proxies={'http': Ipool.get_proxy_random()}, verify=False)
    except:
        response = requests.get('http://search.ccgp.gov.cn/bxsearch', params=params, headers=headers, proxies={'http': Ipool.get_proxy_random()}, verify=False)
    page_re = '<span style="color:#c00000">(.*?)</span>'
    total = re.findall(page_re, response.text)[0]
    return int(total)//20 + 1

def start_re(page, start_time, headers):
    params = {
        'searchtype': '1',
        'page_index': str(page),
        'bidSort': '0',
        'buyerName': '',
        'projectId': '',
        'pinMu': '0',
        'bidType': '0',
        'dbselect': 'bidx',
        'kw': '',
        'start_time': start_time,
        'end_time': start_time,
        'timeType': '6',
        'displayZone': '',
        'zoneId': '',
        'pppStatus': '0',
        'agentName': '',
    }
    try:
        response = requests.get('http://search.ccgp.gov.cn/bxsearch', params=params, headers=headers,
                                proxies={'http': Ipool.get_proxy_random()},
                                verify=False)
    except:
        response = requests.get('http://search.ccgp.gov.cn/bxsearch', params=params, headers=headers,
                                proxies={'http': Ipool.get_proxy_random()},
                                verify=False)
    # print(response.text)
    # return response
    parse(response, headers)

def parse(response, headers):
    tree = etree.HTML(response.text)
    items = tree.xpath('/html/body/div[5]/div[2]/div/div/div[1]/ul/li')
    for item in items:
        url = item.xpath('./a/@href')[0]
        title = item.xpath('./a/text()')[0].strip()
        times = item.xpath('./span/text()[1]')[0]
        bid_type = item.xpath('./span/strong[1]/text()')[0].strip()
        province = item.xpath('./span/a/text()')
        product = item.xpath('./span/strong[2]/text()')[0]
        time, people, proxy = times.split('|')
        pub_time = time.strip().split(' ')[0].replace('.', '-')
        invite_company = people.strip().split('：')[1]
        agency_company = proxy.strip().split('：')[1]
        if province:
            pub_province = single_province(province[0].strip())
        else:
            pub_province = ''
        products = ','.join(product.strip().split('/'))
        meta = {
            'url': url,
            'title': title,
            'pub_time': pub_time,
            'invite_company': invite_company,
            'agency_company': agency_company,
            'bid_type': bid_type,
            'pub_province': pub_province,
            'products': products,
        }
        parse_detail(meta, headers)

def parse_detail(meta, headers):
    try:
        response = requests.get(meta['url'], headers=headers, verify=False
                                ,proxies={'http': Ipool.get_proxy_random()}
                                )
    except:
        response = requests.get(meta['url'], headers=headers, verify=False
                                ,proxies={'http': Ipool.get_proxy_random()}
                                )
    content = response.content.decode('utf-8')
    tree = etree.HTML(content)
    notice_detail = tree.xpath('//*[@id="detail"]/div[2]/div/div[2]/div/div[3]/div')[0]
    notice_detail = etree.tostring(notice_detail).decode('utf-8')
    meta['notice_detail'] = notice_detail
    return meta

if __name__ == '__main__':
    start_time = get_date(1)
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'close',
        'Pragma': 'no-cache',
        'Referer': 'http://search.ccgp.gov.cn/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    pages = int(get_page(start_time, headers))
    # pages = total//20 + 1
    for page in range(1, pages+1):
        aa = start_re(str(page), start_time, headers)
        print(aa)
