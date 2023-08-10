from requests import session


class Gansu:
    def __init__(self):
        pass
        self.session = session()


    def main(self):

        # cookies = {
        #     '4hP44ZykCTt5O': '5qiWZeF9YR3nro8a1g6W7x6mHOF.5qhNHRZmL6rH2m2rPo3eAu3Ump.0jHMPy9Hua0wGpoSyzvnXU5ZHQ.LpKaA',
        #     'JSESSIONID': 'DF446ED1F9432171F060480F5AA5C4C0.tomcat1',
        #     '4hP44ZykCTt5P': 'HZNjipLYQFjpF5JL1cfefbfKM8t_YwvB01lA7K3NzKKEFyTGOsbvhGMUsXkJIyL_57KxdWV1iRtkehSPfR5Jg5KGXTSLx17f1tNKNgTWRLAG8olWvCWpjBh5CSgg48cD.cRYpqYM5x1fjrpS9jdj0Dmr64s5WXUgKDq5NEXYDbIF4G8vBijBrd4FUmGJAbgzZTF6nl2jr4CTzYrz7MSPb2iZZo7P1q_81JY41qybHNG8V.eNNa_L7KjfWGqHrq1uyn07BOeR2UEqL87cdLT7VXGG3a543pxliNsCvfGMC96rsQgHaEKRKUH7NkPoUyZ7EKnJTmnwq.boznHvt30ovcE2HH0NiXIgLF94D3eJrWZqQLIhjhKTc0sPuyNuioryRVqp6gNurQkxyqo9es85GsVUmyAvy5orXaNwonvsA8W',
        # }

        headers = {
            'Host': 'www.ccgp-gansu.gov.cn',
            'Cache-Control': 'max-age=0, no-cache',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://www.ccgp-gansu.gov.cn/',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            # 'Cookie': '4hP44ZykCTt5O=5qiWZeF9YR3nro8a1g6W7x6mHOF.5qhNHRZmL6rH2m2rPo3eAu3Ump.0jHMPy9Hua0wGpoSyzvnXU5ZHQ.LpKaA; JSESSIONID=DF446ED1F9432171F060480F5AA5C4C0.tomcat1; 4hP44ZykCTt5P=HZNjipLYQFjpF5JL1cfefbfKM8t_YwvB01lA7K3NzKKEFyTGOsbvhGMUsXkJIyL_57KxdWV1iRtkehSPfR5Jg5KGXTSLx17f1tNKNgTWRLAG8olWvCWpjBh5CSgg48cD.cRYpqYM5x1fjrpS9jdj0Dmr64s5WXUgKDq5NEXYDbIF4G8vBijBrd4FUmGJAbgzZTF6nl2jr4CTzYrz7MSPb2iZZo7P1q_81JY41qybHNG8V.eNNa_L7KjfWGqHrq1uyn07BOeR2UEqL87cdLT7VXGG3a543pxliNsCvfGMC96rsQgHaEKRKUH7NkPoUyZ7EKnJTmnwq.boznHvt30ovcE2HH0NiXIgLF94D3eJrWZqQLIhjhKTc0sPuyNuioryRVqp6gNurQkxyqo9es85GsVUmyAvy5orXaNwonvsA8W',
            'Pragma': 'no-cache',
        }

        response = self.session.get('https://www.ccgp-gansu.gov.cn/',
                                # cookies=cookies,
                                headers=headers,
                                verify=False
                                )
        print(response.text)


    def get_js(self):

        cookies = {
            '4hP44ZykCTt5O': '5KcobRumXfi0BGTc8OD7Z6Gq6KXp_TGEWDboNl4t0uHP6_I2toxj0NF2fG9xIX2_J193ew5NDQPS8OZ103Pkh0A',
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://www.ccgp-gansu.gov.cn/',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        response = self.session.get('https://www.ccgp-gansu.gov.cn/tQrlMwxgEtCS/xsWaJeZftrRw.11afee1.js',
                                # cookies=cookies,
                                headers=headers,
                                verify=False
                                )
        print(response.text)




if __name__ == '__main__':

    gs = Gansu()
    # gs.main()
    gs.get_js()


