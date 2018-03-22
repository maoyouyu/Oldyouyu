from collections import OrderedDict
from huijiWiki import HuijiWiki
import json


def run_job():
    a_data_page_name = 'Data:Unit_aaa.json'
    a_data = OrderedDict([
        ('name', 'aaa'),
        ('type', 'attacker'),
        ('datatype', 'Unit'),
    ])

    b_data_page_name = 'Data:Unit_bbb.json'
    b_data = OrderedDict([
        ('name', 'bbb'),
        ('type', 'healer'),
        ('datatype', 'Unit'),
    ])

    # 创建wiki对象
    wiki = HuijiWiki('qunxing')
    if not wiki.login('username', 'password'):
        print('登录失败')
        return False

    # 获取token
    if not wiki.get_edit_token():
        print('获取token失败')
        return False

    # 编辑
    # edit参数：
    # title：页面标题
    # text：页面编辑内容
    # 以上两个必填
    # summary：编辑摘要
    # filepath：一个本地文件路径，如果填写的话，页面成功编辑的情况下，会保存编辑内容为一个文本到这个文件
    # compare_flag：布尔值，默认False，如果为True的话，编辑内容会和filepath指定的文本文件进行内容对比，如果一样则跳过上传
    wiki.edit(a_data_page_name, json.dumps(a_data))
    wiki.edit(b_data_page_name, json.dumps(b_data))
    # 等待编辑进程完成
    wiki.wait_threads()

    print('编辑完成')
    return True


if __name__ == '__main__':
    run_job()
