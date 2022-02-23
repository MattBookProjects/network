from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Post
from .views import *
import time

# Create your tests here.
class ViewsTestCase(TestCase):

    def setUp(self):
        a1 = User.objects.create_user(username="user1", password="password")
        a2 = User.objects.create(username="user2")
        a3 = User.objects.create(username="user3")
        p1 = Post.objects.create(author=a1, content="test1")
        Post.objects.create(author=a2, content="test2")
        Post.objects.create(author=a3, content="test3")
        Follow.objects.create(follower=a1, followed=a2)
        

    def test_all_posts_view(self):
        c = Client()
        response = c.get(reverse("all_posts"))
        data = response.json()
        usernames = ["user3", "user2", "user1"]
        contents = ["test3", "test2", "test1"]
        self.assertEqual(len(data), 3)
        for i in range(3):
            self.assertEqual(data[i]["author"]["username"], usernames[i])
            self.assertEqual(data[i]["content"], contents[i])

    def test_following_posts_view(self):
        a1 = User(User.objects.get(username="user1"))
        c = Client()
        c.login(username="user1", password="password")
        response = c.get(reverse("following_posts"))
        #data = response.json()
        #self.assertEqual(len(data), 1)
        #self.assertEqual(data[0]["author"]["username"], "user2")
        #self.assertEqual(data[0]["content"], "test2")
        


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
        
            
        

