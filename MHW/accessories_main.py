#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing 
# Time : 2018/2/16

import requests
from bs4 import BeautifulSoup
from crawl_monster import analysis
from yuee_lib.SaveToExcel import save_to_excel
from collections import OrderedDict
import os


# 获取网页源代码
def getHTMLText(url):

    # 判断网页文件是否存在
    root_html = 'html\\monster' + "\\" + url.split('/')[-2] + "\\" + url.split('/')[-1]
    if os.path.exists(root_html):
        with open(root_html, 'r', encoding="utf-8") as f:
            html = f.read()
        print('文件已存在'+url)
        return html

    else:
        html = saveWeb(url)
        print("文件保存成功！" + url)
        return html


# 首页爬虫
def homeSpider(html):
    url_list = []
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('table', id='sc_12')
    urlSpider = soup('tr')
    for k in range(len(urlSpider)):
            a_list = urlSpider[k].find_all('a')
            for monster_url in a_list:
                a_url = monster_url.attrs
                html = a_url['href']
                url_list.append(html)
    print('首页解析完成')
    return url_list

# 最终页爬虫
def finallySpider(url_list,accessories_list):


    for finallyUrl in url_list:
        # 解析最终页网页地址
        finallyHtml = getHTMLText(finallyUrl)
        finally_dict = analysis(finallyHtml)


        accessories_list.update(finally_dict)

        # 合并表格
        for k, v in finally_dict.items():
            accessories_list[k] = v
        print('表格和并成功' + finallyUrl)


    return accessories_list


# 生成excel数据
def saveExcel(accessories_list):

    data_basename = 'monster'
    headers = OrderedDict([
        (data_basename, [])
        # (data_basename, ['套装名字', 'レア', '性别','装备名字','防御力','强化后','火', '水', '雷','氷', '龍'
        #                  '防御力', '强化后', '火', '水', '雷', '氷', '龍', '技能1', '技能值1', '技能2', '技能值2'
        #                  '技能3', '技能值3', '技能4', '技能值4', '套装技能名称', 'スキル名1', '必要数1', 'スキル名2',
        #                  '必要数2', 'スキル名3', '必要数3', 'スキル名4', '必要数4', 'スキル名5', '必要数5', '各防具生産費用',
        #                  '必要素材1', '必要数量1', '必要素材2', '必要数量2', '必要素材3', '必要数量3', '必要素材4', '必要数量4',
        #                  '必要素材5', '必要数量5',
        #                  ])
    ])
    contents = OrderedDict([
        (data_basename, OrderedDict())
    ])

    for armor_name, armor_info in accessories_list.items():
        for header in armor_info.keys():
            if header not in headers[data_basename]:
                headers[data_basename].append(header)

    contents[data_basename] = accessories_list

    save_filepath = os.path.join(data_basename + '.xlsx')

    save_to_excel(headers, contents, save_filepath)

    print('表格处理我完成')

    x=1

# 创建更改本地路径
def changeRoot(url,root):

    # 根据不同的路径，更改文件路径
    if url.split('/')[-2] == 'data':
        root = root +"\\" + 'data\\'
    elif url.split('/')[-2] == 'ida':
        root = root +"\\" + 'ida\\'

    return root

# 设置超时
def get(url):
    response = None
    for i in range(10):
        try:
            response = requests.get(url, timeout=10)
        except:  # 超时重新下载
            if i == 10:
                print('连续操作超时%d次，操作失败！' % (i + 1))
                return False
            else:
                print('操作超时，正在重试（第%d次）...' % (i + 1))
    return response

# 保存网页
def saveWeb(url):
    root = "html\\monster"
    root = changeRoot(url, root)
    path = root + url.split('/')[-1]
    try:

        if not os.path.exists(root):
            os.mkdir(root)
        if not os.path.exists(path):
            response = get(url)
            if response.status_code == 200:
                with open(path, 'w', encoding="UTF-8") as f:
                    f.write(response.text)

                return response.text
        else:
            print('文件已存在')

    except Exception as e:
        return "出现网页出现错误，请检查"

def main():
    monster_list = OrderedDict()
    f = open('html\【MHW】Monhan World Capture Recipe.html', 'r', encoding="utf-8")
    html = f.read()
    f.close()

    url_list = homeSpider(html)
    # armor_url_list = secondSpider(url_list)
    # finally_url = getHTMLText(armor_url_list)
    finallySpider(url_list,monster_list)
    saveExcel(monster_list)

if __name__ == '__main__':
    main()