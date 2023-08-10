import base64
import requests
import re
from lxml import etree
from fontTools.ttLib import TTFont


url = 'https://xm.58.com/ershouche/?PGTID=0d100000-0025-e7c0-f349-f6fb99ec299a&ClickID=2'
#58反爬比较强，所以我们头全写
headers = {
'authority': 'xm.58.com',
'method': 'GET',
'path': '/ershouche/?PGTID=0d100000-0025-e7c0-f349-f6fb99ec299a&ClickID=2',
'scheme': 'https',
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
'cache-control': 'no-cache',
'cookie': 'f=n; userid360_xml=DF790A407DD312F8230CF109530AC2BD; time_create=1631538931202; commontopbar_ipcity=zhangpu%7C%E6%BC%B3%E6%B5%A6%7C0; myLat=""; myLon=""; id58=r5k1JWEXmnttPtncoqH9+g==; mcity=zhangpu; 58tj_uuid=c72abed3-2489-4e7c-a321-691932bae8d3; wmda_uuid=d82a91d7f9f65ac837bb5b625c7b1068; wmda_new_uuid=1; als=0; xxzl_deviceid=0yvDkPJsU54k1%2BmeRC6Jp43aVt%2Bi7XJ7nI3mjoAoEaBaTbTRjvzYN%2FRqpRUawEXq; sessionid=36b1e461-0f5c-4f3b-ba5b-4eb4c7abd190; fzq_h=9db1bd518df2c5ff11e98c3775bb3bab_1628936871311_d7d3355fc4ca42a7bdb1d0a21f39d5c4_2363523693; f=n; city=xm; 58home=xm; wmda_visited_projects=%3B11187958619315%3B1731916484865%3B1732038237441%3B2385390625025; 58_ctid=606; is_58_pc=1; commontopbar_new_city_info=46%7C%E5%8E%A6%E9%97%A8%7Cxm; ctid=46; aQQ_ajkguid=7A6CE0F2-01D0-978C-9DB3-SX0814211431; sessid=7D16F3E3-652C-5EFB-AD5C-SX0814211431; __xsptplus8=8.1.1628946873.1628946873.1%234%7C%7C%7C%7C%7C%23%23t6AyIlY5mNYqNbQWgTNdey7ludWc_Aq_%23; xxzl_cid=c2bd9243c2614a22a6e811404337c8b6; xzuid=261dd2fa-dd63-49e9-b293-84c4afe5498b; wmda_session_id_1732038237441=1628961854128-e660d3fe-4be8-496b; new_uv=3; utm_source=; spm=; init_refer=https%253A%252F%252Fxm.58.com%252F%253Ffrom%253Dpc_topbar_home%2526PGTID%253D0d3090a7-0025-e161-980b-bb07e2053409%2526ClickID%253D3; new_session=0; fzq_js_usdt_infolist_car=4078e6bf9869aa309438c21d8a1fca5d_1628962005226_2',
'pragma': 'no-cache',
'referer': 'https://xm.58.com/?from=pc_topbar_home&PGTID=0d3090a7-0025-e161-980b-bb07e2053409&ClickID=3',
'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
'sec-ch-ua-mobile': '?0',
'sec-fetch-dest': 'document',
'sec-fetch-mode': 'navigate',
'sec-fetch-site': 'same-origin',
'sec-fetch-user': '?1',
'upgrade-insecure-requests': '1',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67'
}
res = requests.get(url=url,headers=headers)
print(res.text)

base64_content = re.findall("charset=utf-8;base64,(.*?)'",res.text)[0]
byte_content = base64.b64decode(base64_content)
with open('58car.ttf','wb') as f:
    f.write(byte_content)
font = TTFont('58car.ttf')
font.saveXML('58car.xml')
#打印字符对应关系
print(font.getBestCmap())
print(font.getReverseGlyphMap())

#通过自定义字符文件，获取对应字体
def get_car_price(string, font):
    unicode_glyph = font.getBestCmap()
    glyph_price = font.getReverseGlyphMap()
    new_str = ''
    for char in string:
        char_unicode = ord(char)
        if char_unicode in unicode_glyph:
            glyph_code = unicode_glyph[char_unicode]
            price = glyph_price[glyph_code]
            new_str += str(price)

    return new_str

html = etree.HTML(res.text)
car_list = html.xpath('//li[@class="info"]')
for car in car_list:
	#获取汽车名(无字体反爬)
    car_name = car.xpath('./div/a/div/h2/span/text()')[0].strip()
    #获取汽车价格(有字体反爬)
    car_price = car.xpath('./div/a/div/b/text()')[0].strip()
    print('price: ', car_price)
    car_price = get_car_price(car_price,font)

    print('汽车：%s, 价格：%s'%(car_name,car_price))
