#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing 
# Time : 2018/3/22
import time
import requests
from BS4 import BeautifulSoup


def kill_captcha(data):
    with open('captcha.png','wb') as fp:
        fp.write(data)
    return input('captcha:')

def login(username, password, oncaptcha):
    session = requests.session()

    _xsrf = BeautifulSoup(session.get('https://www.zhihu.com/#signin').content).find('input',attes={'name':'_xsrf'})['value']
    data = {
        '_xsrf': _xsrf,
        'email': username,
        'password': password,
        'remever_me':'true',
        'captcha':oncaptcha(captcha_content),
    }

    resp = session.post('http://www,zhihu,com/login/email', data).content
    assert '\u767b\u9646\u6210\u529f' in resp
    return session

if __name__ == '__main__':
    session = login('email', 'password', kill_captcha)
    print(BeautifulSoup(session.get("https://www.zhihu.com").content).find('span', class_='name').getText())
