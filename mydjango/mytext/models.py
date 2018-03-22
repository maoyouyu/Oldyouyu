from django.db import models

# Create your models here.
class article(models.Model):
    title = models.CharField(max_length=50)
    user = models.CharField(max_length=30,
                            )
    body = models.TextField()
