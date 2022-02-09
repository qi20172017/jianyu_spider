
def canyin():
    import requests

    url = "http://lv-api.ulikecam.com/viamaker/v1/category/template/list?device_type=android&viamaker_sdk_version=99.0.0&app_version=6.4.1&aid=1393&viamaker_biz_id=4&viamaker_device_platform=android"

    payload = "{\"cursor\":20,\"pack_option\":{\"is_pack_author\":true},\"count\":20,\"access_key\":\"5d90ec1baaad160e5eb39018cee5af3a\",\"category_id\":10044}"
    headers = {
        'Host': 'lv-api.ulikecam.com',
        'Cookie': 'language=zh;region=CN;envNum=59;envid=1208;envtype=1163',
        'app-type': 'yipai',
        'app-name': 'EasyShoot',
        'app-version': '6.4.1',
        'version-code': '641',
        'device-platform': 'Android',
        'device-id': '2392986422087582',
        'device-info': 'google%2CPixel%2C7.1.2',
        'time': '1622518102310',
        'appliction-name': 'smartcut',
        'os-version': 'REL',
        'did': '2392986422087582',
        'iid': '3184646750474056',
        'channel': 'xiaomi_1393',
        'aid': '1393',
        'device-type': 'Pixel',
        'session-key': '80b1e18304bc39aa3ea96deb826ddcdb',
        'sdk-user-id': '1565303403195975',
        'timestamp': '1622518102',
        'sign': 'fb6812ac2f9ab4714a9b5e23ee61000c',
        'x-vc-bdturing-sdk-version': '2.0.1',
        'Content-Type': 'application/json; charset=utf-8',
        'X-SS-STUB': '735BBC4A6CFCAA9141E54A5A874744CE',
        'x-tt-trace-id': '00-c59d7aa40d8806891a40f9e738810571-c59d7aa40d880689-01',
        'User-Agent': 'com.bytedance.ad.videotool/641 (Linux; U; Android 7.1.2; zh_CN_#Hans; Pixel; Build/N2G47O; Cronet/TTNetVersion:58eeeb7f 2020-11-03 QuicVersion:47946d2a 2020-10-14)',
        'X-Gorgon': '04082893000556199a7ae99eae26bd05d363318bd4073ed5ebca',
        'X-Khronos': '1622518102',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def guanggao():
    import requests

    url = "http://lv-api.ulikecam.com/viamaker/v1/category/template/list?device_type=android&viamaker_sdk_version=99.0.0&app_version=6.4.1&aid=1393&viamaker_biz_id=4&viamaker_device_platform=android"

    payload = "{\"cursor\":40,\"pack_option\":{\"is_pack_author\":true},\"count\":20,\"access_key\":\"5d90ec1baaad160e5eb39018cee5af3a\",\"category_id\":10044}"
    headers = {
        'Host': 'lv-api.ulikecam.com',
        'Cookie': 'language=zh;region=CN;envNum=59;envid=1208;envtype=1163',
        'app-type': 'yipai',
        'app-name': 'EasyShoot',
        'app-version': '6.4.1',
        'version-code': '641',
        'device-platform': 'Android',
        'device-id': '2392986422087582',
        'device-info': 'google%2CPixel%2C7.1.2',
        'time': '1622518462648',
        'appliction-name': 'smartcut',
        'os-version': 'REL',
        'did': '2392986422087582',
        'iid': '3184646750474056',
        'channel': 'xiaomi_1393',
        'aid': '1393',
        'device-type': 'Pixel',
        'session-key': '80b1e18304bc39aa3ea96deb826ddcdb',
        'sdk-user-id': '1565303403195975',
        'timestamp': '1622518462',
        'sign': '4d084eb0053c411738500529a84ab14a',
        'x-vc-bdturing-sdk-version': '2.0.1',
        'Content-Type': 'application/json; charset=utf-8',
        'X-SS-STUB': 'DEECF587FD66BFB06E309960145536A9',
        'x-tt-trace-id': '00-c5a2fa360d8806891a40f9eebb500571-c5a2fa360d880689-01',
        'User-Agent': 'com.bytedance.ad.videotool/641 (Linux; U; Android 7.1.2; zh_CN_#Hans; Pixel; Build/N2G47O; Cronet/TTNetVersion:58eeeb7f 2020-11-03 QuicVersion:47946d2a 2020-10-14)',
        'X-Gorgon': '04082893000556199acf5fd2341dbd05d363318bd4073e15f0bb',
        'X-Khronos': '1622518462',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
