from django.db import models

# Create your models here.

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from taggit.managers import TaggableManager



class PublishedManager(models.Manager):

    def get_queryset(self):
        return super(PublishedManager, self).get_queryset()\
                .filter(status='published')

class Post(models.Model):

    STATUS_CHOIES = (
        ('draft','Draft'),
        ('published','Pulished')
    )

    title = models.CharField(max_length=250)
    slug = models.CharField(max_length = 250,
                            unique_for_date = 'publish')
    author = models.CharField(User,max_length=250)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now= True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOIES,
                              default = 'draft')

    tags = TaggableManager()

    objects = models.Manager()
    published = PublishedManager()

    # tag = TaggableManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.strftime('%m'),
                             self.publish.strftime('%d'),
                             self.slug, ])

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meat:
        ordering = ('reated',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name,self.post)










