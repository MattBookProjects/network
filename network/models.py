from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
   

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2048)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)


    def serialize(self, user):
        return {
            "id": self.id,
            "author": {
                "id": self.author.id,
                "username": self.author.username
            },
            "content": self.content,
            "owned": self.author == user,
            "likes": self.likes.count(),
            "liked": self.likes.filter(id=user.id).count() > 0
        }

class Follow(models.Model):
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followings")