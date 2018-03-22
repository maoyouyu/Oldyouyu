from django.shortcuts import render
from django.http import HttpResponse
from .models import article

# Create your views here.

def article_detail(request, article_id):
    article = article.objects.get(id = article_id)
    return HttpResponse('文章ID： %s', article.title)

def myarticle_list(request,article_id):
    pass

