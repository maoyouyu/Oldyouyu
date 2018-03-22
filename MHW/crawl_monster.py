#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing 
# Time : 2018/2/16

#!/usr/bin/python
#  -*- coding:utf-8 -*-
import re
from bs4 import BeautifulSoup
import requests
import bs4
from yuee_lib.SaveToExcel import save_to_excel
from collections import OrderedDict
import os

def fillUnivList(finallyHtml):
    monster = OrderedDict()


    soup = BeautifulSoup(finallyHtml,'html.parser')
    monsterBasicInformation,name = monsterBasic(soup)
    descriptionInformation = monsterDescription(soup)
    weaknessInformation = monsterWeakness(soup)
    meatinformation = monsterMeat(soup)
    durableInformation = monsterDurable(soup)
    dorpInformation = monsterDrop(soup)
    # 合并表格
    monster[name] = OrderedDict()
    monster[name].update(monsterBasicInformation)
    monster[name].update(descriptionInformation)
    monster[name].update(weaknessInformation)
    monster[name].update(meatinformation)
    monster[name].update(durableInformation)
    monster[name].update(dorpInformation)
    return monster






# 第一行怪物名字以及图片
def monsterBasic(soup):
    name = ""
    informationBasic = OrderedDict()
    monsterInformation = soup.find('div', class_='row_x')

    # 怪物名字信息

    if monsterInformation.find('table', class_='t1')('tr') != None:
        monsterName = monsterInformation.find('table', class_='t1')('tr')
        for i in range(len(monsterName)):
            tr = monsterName[i]
            if i == 0:
                name = tr('td')[0].text.strip()
            th = tr('th')[0].text.strip()
            td = tr('td')[0].text.strip()
            informationBasic[th] = td

    # 怪物图片
    monsterImg_path = (r'G:\youyu\MHW\html\monster\img') + '\\' + name

    monsterImg = monsterInformation.find_all('img')
    for img in range(len(monsterImg)):
        if img == 1:
            monsterImg_path = monsterImg_path + '2.jpg'
        else:
            monsterImg_path = monsterImg_path + '.jpg'

        # 判断图片是否存在
        if not os.path.exists(monsterImg_path):
            monsterImg_url = monsterImg[img].get('src')
            r = requests.get(monsterImg_url)
            with open(monsterImg_path, 'wb') as f:
                f.write(r.content)
                f.close()
                print(name + '图片保存成功')
        else:
            print(name + '图片已存在')

    return informationBasic,name

# 怪物描述
def monsterDescription(soup):
    # description_str = ""
    description = OrderedDict()
    description_soup = soup.find('div', class_='c_box')
    if description_soup != None:
        description_text = description_soup.text
        description_str = cleanWrap(description_text)

        description['怪物描述'] = description_str
    return description

# 怪物弱点
def monsterWeakness(soup):
    # 判断是否存在
    first_status = OrderedDict()
    weaknessSoup = soup.find_all('div', class_='box5')
    if  weaknessSoup != None :
        for box_num in range(len(weaknessSoup)):
            if box_num == 0 :
                weakness_text = weaknessSoup[box_num].text
                weakness = cleanWrap(weakness_text)
                weakness_dict = OrderedDict()
                weakness_dict['弱点描述'] = weakness
                # return weakness_dict

                # 怪物弱点以及状态
                status_dict = OrderedDict()
                # 第一行的状态  # 目前在击打位置上有问题
                status_soup = weaknessSoup[box_num].next_sibling.next_sibling
                first_status = merge_th_td(status_soup)
                # 第二行的状态
                status_soup_second = status_soup.next_sibling.next_sibling
                second_status = merge_th_td(status_soup_second)
                # # 第三行的状态
                try:
                    third_soup = soup.find('div', class_='col-md-6')
                    third_text = third_soup('th')
                    third_text.pop(0)
                    third_td = third_soup('td')
                    for status_num in range(len(third_text)):
                        th = third_text[status_num].text
                        td = cleanWrap(third_td[status_num].text.strip())
                        status_dict[th] = td
                except:
                    print('找不到内容')

                 # 合并三个字典
                first_status.update(second_status)
                first_status.update(status_dict)
                first_status.update(weakness_dict)
            elif box_num == 1 :
                weakness_text = weaknessSoup[box_num].text
                weakness = cleanWrap(weakness_text)
                weakness_dict = OrderedDict()
                weakness_dict['肉质描述'] = weakness
                first_status.update(weakness_dict)

            elif box_num == 2 :
                weakness_text = weaknessSoup[box_num].text
                weakness = cleanWrap(weakness_text)
                weakness_dict = OrderedDict()
                weakness_dict['外观描述'] = weakness
                first_status.update(weakness_dict)



    return first_status

# 肉质
def monsterMeat(soup):
    meat_dict = OrderedDict()
    meat = soup.find('div', class_="col-md-9")
    if  meat != None:
        meat_tr = meat('tr')
        for meat_num in range(len(meat_tr)):
            if meat_num > 1:
                meatAttributes = meat_tr[meat_num]('th')[0].text
                t = meat_tr[meat_num]('td')
                for attached_tag in range(len(meat_tr[1]('th'))):
                    if attached_tag != 0 :
                        meat_key = meatAttributes + "'" + meat_tr[1]('th')[attached_tag].text
                        # t = meat_tr[meat_num]('td')
                        meat_dict[meat_key] = t[attached_tag-1].text
    return meat_dict

# 怪物的耐久值
def monsterDurable(soup):
    durable_dict = OrderedDict()
    durable = soup.find('div', class_='col-md-3 pc_only')
    if durable != None:
        durable_tr = durable('tr')
        # 循环列表
        for durable_num in range(len(durable_tr)):
            if durable_num > 1:
                # 从第二行开始循环
                durableAttributes = durable_tr[durable_num]('th')[0].text
                durable_td = durable_tr[durable_num]('td')
                # 把标题添加给每一个部位
                for durable_tag in range(len(durable_tr[1]('th'))):
                    # 第一个是部位所以不要
                    if durable_tag != 0 :
                        durable_key = durableAttributes + ";" + durable_tr[1]('th')[durable_tag].text
                        # td标签中第一个是数值
                        if durable_tag == 1:
                            durable_dict[durable_key] = durable_td[durable_tag-1].text.strip()
                        #第二个标签是颜色
                        elif durable_tag == 2:
                            color = durable_td[durable_tag-1].get('style').split(':')[-1].split(';')[0]
                            durable_dict[durable_key] = color
    return durable_dict

# 怪物掉落、奖励、任务费
def monsterDrop(soup):
    first_information = OrderedDict()
    second_information = OrderedDict()
    last_information = OrderedDict()
    drop = soup.find_all('table', class_='t1 f_min')

    # 最后的三个表格
    for drop_num in range(len(drop)):
        if drop_num == 0:
            drop_first = drop[drop_num]
            first_information = first_drop(drop_first)
        len_drop = len(drop)
        if len_drop == 4:
        # 网站破坏奖励和捕获/任务费
            if drop_num == 2 or drop_num == 1:
                try:
                    drop_second = drop[drop_num]
                    second_information = second_drop(drop_second)
                    first_information.update(second_information)
                except:
                    print('list index out of range')
            elif drop_num == 3 :
                drop_last = drop[drop_num]
                last_information = last_drop(drop_last)
                first_information.update(last_information)
        # 破坏奖励没有
        elif len_drop == 3:
            if drop_num == 1:
                drop_second = drop[drop_num]
                second_information = second_drop(drop_second)
                first_information.update(second_information)
            elif drop_num == 2:
                drop_last = drop[drop_num]
                last_information = last_drop(drop_last)
                first_information.update(last_information)
        elif len_drop == 2:
            drop_last = drop[drop_num]
            last_information = last_drop(drop_last)
        # first_information.update(second_information)
            first_information.update(last_information)
    return first_information


# 外观任务

def last_drop(drop):
    article_tr = drop('tr')
    last_drop_dict = OrderedDict()
    for article_num in range(len(article_tr)):
        if article_num != 0:
            article_td = article_tr[article_num]('td')
            for td_num in range(len(article_td)):
                if td_num == 0:
                    try:
                        a_text = article_td[td_num]('a')[0].text
                        span_text = article_td[td_num]('span')[0].text

                        th_name = article_tr[0]('th')[0].text

                        last_drop_dict[th_name+ '备注'+str(article_num)] = a_text
                        last_drop_dict[th_name+ '奖励'+str(article_num)] = span_text
                    except:
                        print('list index out of range')

                    # 保存图片
                    img_save = article_td[td_num]('img')
                    savePicture(img_save)
                elif td_num == 1 :
                    img_save = article_td[td_num]('img')
                    if img_save:
                        savePicture(img_save)
                    m = article_td[td_num]('a')
                    if m :
                        a_text = article_td[td_num]('a')[0].text
                        th_name = article_tr[0]('th')[1].text
                        last_drop_dict[th_name + str(article_num)] = a_text

                elif td_num == 2 :
                    img_save = article_td[td_num]('img')
                    if img_save:
                        savePicture(img_save)
                    a_list = article_td[td_num]('a')
                    for a_num in range(len(a_list)):
                        font_list = article_td[td_num]('font')
                        th_name = article_tr[0]('th')[2].text
                        last_drop_dict[th_name + str(article_num)+ ';' + str(a_num)] = a_list[a_num].text
                        if font_list:
                            last_drop_dict[th_name + str(article_num)+ ';' + str(a_num) +'次数'] = font_list[a_num].text
    return last_drop_dict

# 保存图片
def savePicture(img):
    for img_num in range(len(img)):
        img_url = img[img_num].get('src')
        img_name = img_url.split('/')[-1]
        path_img = (r'G:\youyu\MHW\html\monster\images') + '\\' + img_name
        try:
            if not os.path.exists(path_img):
                r = requests.get(img_url)
                with open(path_img, 'wb') as f:
                    f.write(r.content)
                    f.close()
                    print(img_name + '图片保存成功')
            else:
                print(img_name + '图片已存在')

        except Exception as e:
            return "出现网页出现错误，请检查"
# 剥离材料
def first_drop(drop):
    # 取出tr标签
    article_tr = drop('tr')
    first_drop_dict = OrderedDict()
    # 每次循环tr标签
    for article_num in range(len(article_tr)):
        if article_num != 0:
            article_td = article_tr[article_num]('td')

            # 一次循环中的名字,以及可剥离次数
            # 备注
            if article_tr[article_num].find('span', class_='c_g b') == None:
                article_name = article_tr[article_num-1].find('span', class_='c_g b').text
                first_drop_dict[str(article_name)+'剥落备注'] = cleanWrap(article_tr[article_num].text)
            else:
                article_name = article_tr[article_num].find('span', class_='c_g b').text
                article_time = article_tr[article_num].find('span', class_='c_p').text
                first_drop_dict['掉落物'+ str(article_num) + '名字'] = article_name
                first_drop_dict[str(article_name) + '可剥离次数'] = article_time
                # 掉落物
                for td_num in range(len(article_td)):
                    if td_num != 0 :
                        article_a = article_td[td_num]('a')
                        article_span = article_td[td_num]('span')
                        # 循环上下位
                        for a_num in range(len(article_a)):
                            if article_a[a_num] != None:
                                try:
                                    title_str = ";" + article_tr[0]('th')[td_num].text
                                    crticle_str = '剥离'+ str(article_name)+ '掉落物品'+ str(a_num) + title_str
                                    probability_str = '剥离'+ str(article_name)+ '掉落几率'+ str(a_num) + title_str
                                    first_drop_dict[crticle_str] = article_a[a_num].text
                                    first_drop_dict[probability_str] = article_span[a_num].text
                                except:
                                    print('list index out of range')
    return first_drop_dict

# 第二个和第三个的表格解析
def second_drop(drop):

    # 取出tr标签
    article_tr = drop('tr')
    second_drop_dict = OrderedDict()
    # 每次循环tr标签
    for article_num in range(len(article_tr)):

        if article_num != 0:
            article_td = article_tr[article_num]('td')

            # 一次循环中的名字,以及可剥离次数
            # 备注
            if article_tr[article_num].find('span', class_='c_g b') == None:
                # 怪物名称
                article_name = article_tr[article_num-1].find('span', class_='c_g b').text + str(article_num-1)
                second_drop_dict[str(article_name)+'报酬备注'] = cleanWrap(article_tr[article_num].text)
            else:
                # 怪物名称
                article_name = article_tr[article_num].find('span', class_='c_g b').text + str(article_num)

                second_drop_dict['报酬物'+ str(article_num) + '名字'] = article_name

                # 掉落物
                for td_num in range(len(article_td)):
                    if td_num != 0 :
                        article_a = article_td[td_num]('a')
                        article_span = article_td[td_num]('span')
                        # 循环上下位
                        for a_num in range(len(article_a)):
                            title_str = ";" + article_tr[0]('th')[td_num].text
                            crticle_str = str(article_name)+ '物品'+ str(a_num) + title_str
                            probability_str = str(article_name)+ '几率'+ str(a_num) + title_str
                            second_drop_dict[crticle_str] = article_a[a_num].text
                            second_drop_dict[probability_str] = article_span[a_num].text
    return second_drop_dict



# 小工具 第一行为key，第二行为value
def merge_th_td(status_soup):
    status_dict = OrderedDict()
    status_th = status_soup('th')
    status_td = status_soup('td')
    try:
        for status_num in range(len(status_th)):
            th = status_th[status_num].text
            td = cleanWrap(status_td[status_num].text.strip())
            status_dict[th] = td
    except:
        print('list index out of range')
    return status_dict




# 小工具 去除换行符
def cleanWrap(str):
    change_str = ""
    change_dict = str.split('\n')
    for x in change_dict:
        # 去字符串中空格
        x = x.strip()
        if x == "":
            continue
        else:
            change_str = change_str + x
    return change_str



def analysis(finallyHtml):
    #
    # f = open(r'html\monster\data\3200.html', 'r', encoding="utf-8")
    # finallyHtml = f.read()
    # f.close()
    finally_list = fillUnivList(finallyHtml)
    return finally_list
    # test()

if __name__ == '__main__':
    analysis()


