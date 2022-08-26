from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

from model.msql.my_dao.my_csdn_dao import MyCsdnDao

app = Flask(__name__,)

# http://127.0.0.1:5000/reg


@app.route('/reg')
def reg_view():
    return render_template('register.html')

# 127.0.0.1:5000/check_uname


@app.route('/check_uname')
def check_view():
    # 模拟出一个用户列表
    ulist = ['貂蝉', '王昭君', '妲己', '赵云']
    # 当前端get请求发送时
    if request.method == 'GET':
        # 接收前端的数据 uname
        uname = request.args.get('uname')
        # 判断uname是否为空
        # 判断uname是否在ulist中
        if uname in ulist:
            # 如果在 返回 '用户名已存在'
            return '1'
        else:
            # 否则  返回  '用户名可以使用'
            return '0'

# 127.0.0.1:5000/get_user


@app.route('/get_user')
def get_user():
    return render_template('get-user.html')

# 127.0.0.1:5000/get_user_server


@app.route('/get_user_server')
def get_user_server():
    # id_uname_pwd|id_uname_pwd|...

    data = [
        {'id': '1', 'uname': 'bob', 'pwd': '123456'},
        {'id': '2', 'uname': 'tom', 'pwd': '123123'},
        {'id': '3', 'uname': 'hanmeimei', 'pwd': '000000'}
    ]
    # return '1_bob_123456|2_tom_123123|3_hanmeimei_000000'
    # separators=(',',':')   默认值(', ',': ')默认值带有多余的空格
    # sort_keys 对数据的键做排序
    # return json.dumps(data,separators=(',',':'),sort_keys=True)
    result = MyCsdnDao.get('18987865@1644473472241')

    data = [
        {'id':result['item_id'],'uname':result['author'], 'pwd':result['url']}
    ]

    print(result)
    return jsonify(data)

# 127.0.0.1:5000/post_json


@app.route('/post_json')
def post_json():
    return render_template('post-json.html')


# {"uname":"shibw","pwd":"123456"}:
# uname : "shibw"
@app.route('/post_json_server', methods=['post'])
def post_json_server():
    # uname = request.get_json('uname')
    json_str = request.get_json()
    print(request.json)
    # print(request.get_data())
    # print(json_str)
    print(json_str.get('uname'))
    uname = json_str.get('uname')
    pwd = json_str.get('pwd')

    if uname == 'laowang' and pwd == '123456':
        # 登录失败对于浏览器来说是正常的响应
        # 但是对于程序逻辑来说是失败的操作
        # 考虑自定义状态码 告诉前端目前程序的结果
        data = {'code': 200, 'msg': 'OK'}
        return jsonify(data)
    else:
        data = {'code': 201, 'msg': '登录失败'}
        return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
