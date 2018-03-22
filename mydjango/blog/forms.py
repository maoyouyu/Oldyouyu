#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Dong-Qing 
# Time : 2018/3/13

from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length =30)
    email = forms.EmailField()
    to = forms.EmailField()
    cmments = forms.CharField(required=False,
                              widget=forms.Textarea)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('name','email','body')

