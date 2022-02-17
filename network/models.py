from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField('self', on_delete=models.CASCADE, related_name='followers')

class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2048)
    likers = models.ManyToManyField(User, on_delete=models.CASCADE, related_name='liked_posts')
    


