from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField('self', related_name='followers')
    following_count = models.IntegerField(default=0, blank=True)
    followers_count = models.IntegerField(default=0, blank=True)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2048)
    likers = models.ManyToManyField(User, related_name='liked_posts')
    likes = models.IntegerField(default=0, blank=True)



