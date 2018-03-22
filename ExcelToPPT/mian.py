#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing 
# Time : 2018/3/7
import os
from Excel import Pyxlchart
from text import text


def mian():
    # rootdir = input('请复制文件夹目录：')
    # pptdir = input('请输入ppt文件所在目录：')
    rootdir =r'G:\youyu\ExcelToPPT\excel'
    list = os.listdir(rootdir)

    # 测试
    # text_name = text()
    # text_name.name = 234
    # bbb = text_name.print_name()

    for file in list:
        if file.split('.')[-1] == 'xlsm' and 'slsx':
            xl = Pyxlchart()
            xl.WorkbookDirectory = rootdir + '\\'
            xl.WorkbookFilename = file.split('$')[-1]
            xl.SheetName = file.split('$')[-1].split('（')[0].replace('进度报告','周进度表').strip()
            xl.ImageFilename = file.split('$')[-1].split('（')[0].strip()
            xl.ExportPath = rootdir
            xl.ChartName = "123"
            xl.start_export()










    x = 1
mian()