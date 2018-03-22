#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing 
# Time : 2018/3/5

from openpyxl import Workbook
from openpyxl.chart import BarChart, Series, Reference

# class text(object):
#     def __init__(self):
#         self.name = ""
#
#     def print_name(self):
#         f = self.name
#         print(self.name)
#         return self.name
# if __name__ == '__main__':
#     xl = text()
#     xl.name = 123
#     # xl.print_name()


num_list = [0.01,0.01,0.02,0.02,0.01,0.03,0.04,0.04,0.01,0.02,0.03,0.04,0.05,0.01]
time = 0

def text1(num_list,time):
    for i in range(len(num_list)):
        if num_list[i] >= 0.02:
            # num_list[i:]
            # for j in range(len(num_list[i:])):
            #     if num_list
            if num_list[i+1] <0.02:
                time = time + 1

    print(time)

text1(num_list,time)