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
    armor = OrderedDict()
    attributes = OrderedDict()
    temporary = []
    soup = BeautifulSoup(finallyHtml,'html.parser')

    # 截取套装名字
    setName = soup.h2.string
    attributes['套装名字'] = setName[:-8]

    # 查找防具数值
    soup = soup.find_all('table',class_='t1')

    # # 第一张表
    tr0 = soup[0]
    tr0 = tr0('td')
    attributes['レア'] = tr0[0].text.strip()
    attributes['性别'] = tr0[1].text.strip()

    # # 第二张表
    tr1 = soup[1]
    tr1 = tr1('tr')
    for i in range(len(tr1)):
        if i == 0 or i == len(tr1)-1:
            pass
        else:
            # 写入每一个装备的名字
            armorName = tr1[i]('td')
            name = str(armorName[0].text.strip())

            # 把名字存入列表方便以后调用
            temporary.append(name)

            # 存入装备信息
            armor[name] = OrderedDict()
            armor[name]['装备名字'] = armorName[0].text.strip()
            armor[name]['防御力'] = armorName[1].text.strip()
            armor[name]['强化后'] = armorName[2].text.strip()
            armor[name]['火'] = armorName[3].text.strip()
            armor[name]['水'] = armorName[4].text.strip()
            armor[name]['雷'] = armorName[5].text.strip()
            armor[name]['氷'] = armorName[6].text.strip()
            armor[name]['龍'] = armorName[7].text.strip()


    # 第三张表
    tr2 = soup[2]
    tr2 = tr2('tr')
    for j in range(len(tr2)):
        if j == 0 or j == len(tr2)-1:
            pass
        else:
            armorName = tr2[j]('td')

            # 转换①，②，③
            socket = ""
            socket_info = armorName[1].text.strip()
            for i in range(len(socket_info)):

                char = list(socket_info)[i]
                if char == '-':
                    socket = socket + '0'
                elif char == " ":
                    socket = socket + ';'
                elif char == '①':
                    socket = socket + '1'
                elif char == '②':
                    socket = socket + '2'
                elif char == '③':
                    socket = socket + '3'
            armor[armorName[0].text.strip()]['孔数'] = socket

            # 添加技能
            skill = armorName[2].text.split('\n')
            # 去除空字符串
            skill = [x for x in skill if x != '' ]

            x = 'fdsfds'

            for num in range(len(skill)):
                if num == 0:
                    armor[armorName[0].text.strip()]['技能1'] = skill[num]
                elif num == 1:
                    armor[armorName[0].text.strip()]['技能值1'] = skill[num]
                elif num == 2:
                    armor[armorName[0].text.strip()]['技能2'] = skill[num]
                elif num == 3:
                    armor[armorName[0].text.strip()]['技能值2'] = skill[num]
                elif num == 4:
                    armor[armorName[0].text.strip()]['技能3'] = skill[num]
                elif num == 5:
                    armor[armorName[0].text.strip()]['技能值3'] = skill[num]
                elif num == 6:
                    armor[armorName[0].text.strip()]['技能4'] = skill[num]
                elif num == 7:
                    armor[armorName[0].text.strip()]['技能值4'] = skill[num]


    # 第四张表
    if len(soup) == 7:
      tr3 = soup[-3]
      tr3 = tr3('tr')


      # 套装效果名字
      name = (tr3[1]('td'))[0].text
      # attributes['套装技能'] = {}
      # attributes['套装技能']['名字'] = name
      for i in range(len(tr3)):
          armorName = tr3[i]('td')

          if len(armorName) == 3:

              for j in range(len(armorName)):
                  if j == 0:
                      attributes['套装技能名称'] = name
                  elif j == 1:
                      attributes['スキル名' + str(i)] = armorName[j].text.strip()
                  elif j == 2:
                      attributes['必要数' + str(i)] = armorName[j].text.strip()

          elif len(armorName) == 2:
              for j in range(len(armorName)):
                  if j == 0:
                      attributes['スキル名' + str(i)] = armorName[j].text.strip()
                  elif j == 1:
                      attributes['必要数' + str(i)] = armorName[j].text.strip()
    else:
        pass


    # 第五张表
    tr4 = soup[-2]
    tr4 = tr4('td')
    attributes['各防具生産費用'] = tr4[0].text.strip()

    # 第六张表
    tr5 = soup[-1]
    tr5 = tr5('tr')
    sub_num = 0

    for sub in range(len(tr5)):
        if sub == 0 or sub == len(tr5)-1 :
            continue
        else:

            # 声明列表
            # armor[temporary[sub_num]]['必要素材'] = {}
            num_n = 0

            # 取出分成小列表项
            armorName = tr5[sub]('td')
            # armorName = armorName.text.strip()
            material = armorName[1].text.split('\n')

            for x in material:
                # 去空字符串
                x = x.strip()
                # 按照 x 分割字符串
                if x == "":
                    continue
                else:
                    materialName = x.split(" x")
                    materialName = [x for x in materialName if x != '']

                    # 循环取出每一项插入列表中
                    for num in range(len(materialName)):
                        if num == 1:

                            n = '必要数量' + str(num_n)
                            armor[temporary[sub_num]][n] = materialName[num]
                        else:
                            num_n = num_n + 1
                            s = '必要素材' + str(num_n)
                            armor[temporary[sub_num]][s] = materialName[num]
            sub_num = sub_num + 1

    # 把attributes插入每一个armor中
    armor_dict = OrderedDict()

    for k, armor1 in armor.items():
        armor_dict[k] = OrderedDict()
        for i, v in armor1.items():
            armor_dict[k][i] = v
        for i, v in attributes.items():
            armor_dict[k][i] = v
    return armor_dict

x=1









# def printUnivList(ulist):
#     pass


def analysis():

    f = open(r'html\ida\226846.html', 'r', encoding="utf-8")
    finallyHtml = f.read()
    f.close()
    finally_list = fillUnivList(finallyHtml)
    return finally_list
    # test()

    # printUnivList(uinfo)
if __name__ == '__main__':
    analysis()


