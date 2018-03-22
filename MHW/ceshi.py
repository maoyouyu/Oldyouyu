import requests
import bs4
from yuee_lib.SaveToExcel import save_to_excel
from collections import OrderedDict
import os


def test():
    # 生成excel数据
    data_basename = '防具'
    headers = OrderedDict([
        (data_basename, ['a', 'c', 'd','X','d','e','f'])
    ])
    contents = OrderedDict([
        (data_basename, OrderedDict())
    ])

    # data = OrderedDict([
    #     ('das', 'dsadasda'),
    # ])
    # data = {
    #     'das': 'asdasd',
    # }

    data = OrderedDict([
        ('X', OrderedDict([
            ('a', 1),
            ('b', 50),
            ('c', 'my name is X'),
        ])),
        ('Y', OrderedDict([
            ('a', 51),
            ('b', 560),
            ('c', 'my name is Y'),
        ])),
        ('x', OrderedDict([
            ('a', 16),
            ('b', 507),
            ('c', 'my name is Z'),
        ])),
    ])

    contents[data_basename] = data

    save_filepath = os.path.join(data_basename + '.xlsx')

    save_to_excel(headers, contents, save_filepath)

test()

x= 1