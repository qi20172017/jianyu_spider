from app.moen_app import moenApp


def send_tu8tu():

    tag_list = [
        # '摩恩',
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



if __name__ == '__main__':
    send_tu8tu()
    # send_haozu()