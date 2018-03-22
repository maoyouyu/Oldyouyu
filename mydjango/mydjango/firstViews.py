#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing 
# Time : 2018/3/9

from django.http import HttpResponse

def index(request):
    return HttpResponse('正在施工...')