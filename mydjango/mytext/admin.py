from django.contrib import admin
from .models import article
# Register your models here.

# class ArticleAdmin(self):
#     def __set__(self):
#         pass


admin.site.register(article)

