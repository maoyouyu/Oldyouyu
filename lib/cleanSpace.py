#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing 
# Time : 2018/3/22


# 去除字符串中的空格
def cleanSpace(str):
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