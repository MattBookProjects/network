from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from .models import User, Post
from .views import *
import time

# Create your tests here.
class ViewsTestCase(TestCase):

    def setUp(self):
        a1 = User.objects.create_user(username="user1", password="password1")
        a2 = User.objects.create_user(username="user2", password="password2")
        a3 = User.objects.create_user(username="user3", password="password3")
        Post.objects.create(author=a1, content="post1")
        Post.objects.create(author=a2, content="post2")
        Post.objects.create(author=a3, content="post3")
        Follow.objects.create(follower=a1, followed=a2)
        self.client = Client()

    def test_login_view(self):
        self.assertTrue(self.client.login(username="user1", password="password1"))
        self.assertFalse(self.client.login(username="user1", password=""))
        self.assertFalse(self.client.login(username="user1", password="password2"))
        self.assertFalse(self.client.login(username="", password="password1"))
        self.assertFalse(self.client.login(username="", password=""))

    def test_register(self):
        get_response = self.client.get(reverse("register"))
        self.assertTemplateUsed(get_response, "network/register.html")
        self.client.post(reverse("register"), {
            "username": "user4",
            "email": "4@mail.com", 
            "password": "password4",
            "confirmation": "password4"})
        self.assertEqual(User.objects.all().count(), 4)
        self.client.post(reverse("register"), {
            "username": "user5",
            "email": "5@mail.com", 
            "password": "password5",
            "confirmation": "password"})
        self.assertEqual(User.objects.all().count(), 4)

class AllPostsViewTestCase(ViewsTestCase):

    def test_all_posts_view(self):
        response = self.client.get(reverse("all_posts"))
        data = response.json()
        usernames = ["user3", "user2", "user1"]
        contents = ["post3", "post2", "post1"]
        self.assertEqual(len(data), 3)
        for i in range(3):
            self.assertEqual(data[i]["author"]["username"], usernames[i])
            self.assertEqual(data[i]["content"], contents[i])

class FollowingPostsViewTestCase(ViewsTestCase):

    def test_following_posts_view(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("following_posts"))
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["author"]["username"], "user2")
        self.assertEqual(data[0]["content"], "post2")
    
    def test_following_posts_view_no_followed(self):
        self.client.login(username="user2", password="password2")
        response = self.client.get(reverse("following_posts"))
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_following_posts_view_not_logged_in(self):
        response = self.client.get(reverse("following_posts"))
        self.assertEqual((response.status_code, response.url), (302, "/login/?next=/posts/following"))
    
class ModelsTestCase(TestCase):

    def setUp(self):
        a1 = User.objects.create_user(username="user1", password="password1")
        a2 = User.objects.create_user(username="user2", password="password2")
        a3 = User.objects.create_user(username="user3", password="password3")
        p11 = Post.objects.create(author=a1, content="post11")
        p12 = Post.objects.create(author=a1, content="post12")
        p2 = Post.objects.create(author=a2, content="post2")
        Follow.objects.create(follower=a1, followed=a2)
        Follow.objects.create(follower=a1, followed=a3)
        Follow.objects.create(follower=a2, followed=a3)
        a1.liked_posts.add(p2)
        a2.liked_posts.add(p11)
        a3.liked_posts.add(p11)

class PostModelTestCase(ModelsTestCase):

    def test_post_serialize_owned(self):
        post = Post.objects.get(id=1)
        user = User.objects.get(username="user1")
        actual = post.serialize(user)
        expected = {
            "id": 1,
            "author": {
                "id": 1,
                "username": "user1"
            },
            "content": "post11",
            "owned": True,
            "likes": 2,
            "liked": False
        }
        self.assertEqual(actual, expected)

    def test_post_serialize_liked(self):
        post = Post.objects.get(id=1)
        user = User.objects.get(username="user2")
        actual = post.serialize(user)
        expected = {
            "id": 1,
            "author": {
                "id": 1,
                "username": "user1"
            },
            "content": "post11",
            "owned": False,
            "likes": 2,
            "liked": True
        }
        self.assertEqual(actual, expected)

    def test_post_serialize_not_liked(self):
        post = Post.objects.get(id=2)
        user = User.objects.get(username="user2")
        actual = post.serialize(user)
        expected = {
            "id": 1,
            "author": {
                "id": 1,
                "username": "user1"
            },
            "content": "post11",
            "owned": False,
            "likes": 2,
            "liked": False
        }
        self.assertEqual(actual, expected)

class UserModelTestCase(ModelsTestCase):
    pass
'''
    def test_user_serialize(self):
        a1 = User.objects.get(username="user1")
        expected = {
            "username": "user1", 
            "id": 1, 
            "own": False, 
            "followers": 0, 
            "followings": 2, 
            "followed": False, 
            "posts": [
                {
                    "id": 1
                    "author": {
                        "id": 1, 
                        "username": "user1"
                    },
                    "content": "post11", 
                    ""}]}
'''
    
      

  


#    def test_following_posts(self):
 #       a1 = User.objects.get(username="user1")
  #      a2 = User.objects.get(username="user2")
   #     a1.following.add(a2)
    #    c = Client({"user": a1})
     #   response = c.get(reverse("following_posts"))
      #  data = response.json()
       # self.assertEqual(len(data), 2)

   # def test_follow(self):
   #     a1 = User.objects.get(username="user1")
   #     a2 = User.objects.get(username="user2")
   #     c = Client()
   #     c.put(reverse("profiles", kwargs={'id': 3}))
        
            
        

