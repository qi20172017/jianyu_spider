from app.moen_app import moenApp


def send_tu8tu():

    tag_list = [
                '摩恩',
                '九牧',
                '恒洁',
                '科勒',
                '汉斯格雅',
                '高仪',
                'TOTO',
                '箭牌',
                'Moen',
                'JOMOO',
                'HEGII',
                'Kohler',
                'hansgrohe',
                'GROHE',
                'ARROW',
                ]
    for tag in tag_list:
        moenApp.send_task("moen.tu8tu.list", args=(1, tag))

def send_haozu():

    tag_list = [
                '摩恩',
                '九牧',
                '恒洁',
                '科勒',
                '汉斯格雅',
                '高仪',
                'TOTO',
                '箭牌',
                'Moen',
                'JOMOO',
                'HEGII',
                'Kohler',
                'hansgrohe',
                'GROHE',
                'ARROW',
                ]
    for tag in tag_list:
        moenApp.send_task("moen.haozu.list", args=(1, tag))

def send_csdn():
    # moenApp.send_task("moen.csdn.article", args=('kdl_csdn', 1))
    # moenApp.send_task("moen.csdn.article", args=('zjq592767809', 1))
    moenApp.send_task("moen.csdn.article", args=('qq523176585', 1))

def send_sogou():
    author_list = [
        '菜鸟学Python编程',
        '网虫Spider',
        'python爬虫人工智能大数据',
        '进击的Coder',
        '看雪学院',
        'Python进击者',
        '咸鱼学Python',
        'K哥爬虫',
        'feapder爬虫教程',
        '逆向简史',
        '逆向lin狗',
        '大数据安全技术学习',
        'python爬虫与js逆向',
        'Python爬虫scrapy',
        '爬了么',
        '爬小虫联盟',
        'python和逆向',
        'Coder小Q',
        'NightTeam',
        '穿甲兵',
        '爬虫术与道',
        'python网络爬虫大数据与逆向工程',

    ]
    for author in author_list:
        moenApp.send_task("moen.sogou.article", args=(author,))

if __name__ == '__main__':
    # send_tu8tu()
    # send_haozu()
    # send_csdn()
    send_sogou()