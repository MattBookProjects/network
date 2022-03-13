from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    
    def serialize(self, request_user):
        user = {
            "id": self.id,
            "username": self.username,
            "followers": self.followers.all().count(),
            "followings": self.followings.all().count(),
            "posts": [post.serialize(request_user) for post in self.posts.all()]
            }
        if request_user.is_authenticated:
            meta = {
                "authenticated": True,
                "own": self == request_user,
                "followed": self.followers.filter(follower=request_user).count() > 0
                }
        else:
            meta = {
                "authenticated": False
            }
        return {
            "user": user,
            "meta": meta
        }
   

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2048)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)


    def serialize(self, request_user):
        post = {
            "id": self.id,
            "author": {
                "id": self.author.id,
                "username": self.author.username
            },
            "content": self.content,
            "likes": self.likes.count()
        }

        if request_user.is_authenticated:
            meta = {
                "authenticated": True,
                "owned": self.author == request_user,
                "liked": self.likes.filter(id=request_user.id).count() > 0
            }
        else:
            meta = {
                "authenticated": False
            }
        return {
          "post": post,
          "meta": meta
        }

class Follow(models.Model):
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followings")