import re
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import AnonymousUser 
from .models import User, Post
from .views import *
from .urls import *
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
            self.assertEqual(data[i]["post"]["author"]["username"], usernames[i])
            self.assertEqual(data[i]["post"]["content"], contents[i])

class FollowingPostsViewTestCase(ViewsTestCase):

    def test_following_posts_view(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")
        Follow.objects.create(follower=user1, followed=user2)
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("following_posts"))
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["post"]["author"]["username"], "user2")
        self.assertEqual(data[0]["post"]["content"], "post2")
    
    def test_following_posts_view_no_followed(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("following_posts"))
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_following_posts_view_not_logged_in(self):
        response = self.client.get(reverse("following_posts"))
        self.assertEqual((response.status_code, response.url), (302, f"{reverse('login')}/?next={reverse('following_posts')}"))

class ProfilesViewTestCase(ViewsTestCase):

    def test_profiles_view_invalid_method(self):
        user = User.objects.get(username="user1")
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse("profiles", kwargs={"id": user.id}))
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Invalid request method"))

    def test_get_profile_correct(self):
        user = User.objects.get(username="user1")
        response = self.client.get(reverse("profiles", kwargs={"id": user.id}))
        self.assertEqual(response.status_code, 200)

    def test_get_profile_not_found(self):
        id = User.objects.order_by("-id").first().id + 1
        response = self.client.get(reverse("profiles", kwargs={"id": id}))
        self.assertEqual((response.status_code, response.json()["message"]), (404, "Profile not found"))

    def test_follow_profile_not_authenticated(self):
        user = User.objects.get(username="user1")
        response = self.client.put(reverse("profiles", kwargs={"id": user.id}), {"follow": True}, content_type="application/json")
        self.assertEqual((response.status_code, response.url), (302, f"{reverse('login')}/?next={reverse('profiles', kwargs={'id': user.id})}"))

    def test_follow_profile_own(self):
        user = User.objects.get(username="user1")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("profiles", kwargs={"id": user.id}))
        self.assertEqual((response.status_code, response.json()["message"]), (400, "You can't follow your own profile"))

    def test_follow_profile_no_request_body(self):
        user = User.objects.get(username="user2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("profiles", kwargs={"id": user.id}))
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Missing request body"))

    def test_follow_profile_no_follow_parameter(self):
        user = User.objects.get(username="user2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("profiles", kwargs={"id": user.id}), {"data": "value"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Missing follow parameter"))

    def test_follow_profile_invalid_follow_parameter(self):
        user = User.objects.get(username="user2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("profiles", kwargs={"id": user.id}), {"follow": "fdsfsdgs"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Invalid follow parameter"))

    def test_follow_profile_correct(self):
        user = User.objects.get(username="user2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("profiles", kwargs={"id": user.id}), {"follow": True}, content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_unfollow_profile_correct(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")
        Follow.objects.create(follower=user1, followed=user2)
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("profiles", kwargs={"id": user2.id}), {"follow": False}, content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_follow_profile_already_followed(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")
        Follow.objects.create(follower=user1, followed=user2)
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("profiles", kwargs={"id": user2.id}), {"follow": True}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (409, "You already follow this profile"))
    
    def test_unfollow_profile_already_unfollowed(self):
        user = User.objects.get(username="user2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("profiles", kwargs={"id": user.id}), {"follow": False}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (409, "You already don't follow this profile"))

class PostsViewTestCase(ViewsTestCase):

    def test_like_post_correct(self):
        user = User.objects.get(username="user1")
        post = Post.objects.get(content="post2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "like", "like": True}, content_type="application/json")
       # print(response.json()["message"])
        self.assertEqual(response.status_code, 204)

    def test_unlike_post_correct(self):
        user = User.objects.get(username="user1")
        post = Post.objects.get(content="post2")
        post.likes.add(user)
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "like", "like": False}, content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_like_post_already_liked(self):
        user = User.objects.get(username="user1")
        post = Post.objects.get(content="post2")
        post.likes.add(user)
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "like", "like": True}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (409, "You already like this post"))

    def test_unlike_post_already_unliked(self):
        user = User.objects.get(username="user1")
        post = Post.objects.get(content="post2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "like", "like": False}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (409, "You already don't like this post"))

    def test_like_post_no_like_parameter(self):
        post = Post.objects.get(content="post2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "like"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Missing like parameter"))
    
    def test_like_post_invalid_like_parameter(self):
        post = Post.objects.get(content="post2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "like", "like": "sadgsfs"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Invalid like parameter"))

    def test_edit_post_correct(self):
        user = User.objects.get(username="user1")
        post = Post.objects.get(author=user)
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "edit", "content": "newcontent1"}, content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_edit_post_not_owned(self):
        user = User.objects.get(username="user1")
        post = Post.objects.get(author=user)
        self.client.login(username="user2", password="password2")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "edit", "content": "newcontent1"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (403, "You can only edit your own posts"))

    def test_edit_post_no_content_parameter(self):
        user = User.objects.get(username="user1")
        post = Post.objects.get(author=user)
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "edit"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Missing content parameter"))
    
    def test_posts_view_no_request_body(self):
        post = Post.objects.get(content="post2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}))
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Missing request body"))

    def test_posts_view_no_mode_parameter(self):
        post = Post.objects.get(content="post2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"data": "value"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Missing mode parameter"))

    def test_posts_view_invalid_mode_parameter(self):
        post = Post.objects.get(content="post2")
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}), {"mode": "fdjfk"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Invalid mode parameter"))

    def test_posts_view_user_not_authenticated(self):
        post = Post.objects.get(content="post2")
        response = self.client.put(reverse("posts", kwargs={"id": post.id}))
        self.assertEqual((response.status_code, response.url), (302, f"{reverse('login')}/?next={reverse('posts', kwargs={'id': post.id})}"))

    def test_posts_view_post_not_found(self):
        id = Post.objects.order_by('-id').first().id + 1
        self.client.login(username="user1", password="password1")
        response = self.client.put(reverse("posts", kwargs={'id': id}))
        self.assertEqual((response.status_code, response.json()["message"]),(404, "Post not found"))

    def test_posts_view_invalid_method(self):
        post = Post.objects.get(id=1)
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("posts", kwargs={'id': post.id}))
        self.assertEqual((response.status_code, response.json()["message"]),(400, "PUT method required"))

class PostViewTestCase(ViewsTestCase):

    def test_post_view_user_not_authenticated(self):
        response = self.client.post(reverse("post"))
        self.assertEqual((response.status_code, response.url), (302, f"{reverse('login')}/?next={reverse('post')}"))

    def test_post_view_invalid_method(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("post"))
        self.assertEqual((response.status_code, response.json()["message"]), (400, "POST method required"))
    
    def test_post_view_no_request_body(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse("post"))
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Missing request body"))

    def test_post_view_no_content_parameter(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse("post"), {"data": "value"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (400, "Missing content parameter"))

    def test_post_view_correct(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse("post"), {"content": "value"}, content_type="application/json")
        self.assertEqual((response.status_code, response.json()["message"]), (201, "Post created successfully"))

    
class ModelsTestCase(TestCase):

    def setUp(self):
        u1 = User.objects.create_user(username="user1", password="password1")
        u2 = User.objects.create_user(username="user2", password="password2")
        u3 = User.objects.create_user(username="user3", password="password3")
        Post.objects.create(author=u1, content="post11")
        Post.objects.create(author=u1, content="post12")
        Post.objects.create(author=u2, content="post2")
       

class PostModelTestCase(ModelsTestCase):

    def test_post_serialize_post(self):
        post = Post.objects.get(id=1)
        actual = post.serialize(AnonymousUser())["post"]
        expected = {
            "id": 1,
            "author": {
                "id": 1,
                "username": "user1"
            },
            "content": "post11",
            "likes": 0
        }
        self.assertEqual(actual, expected)

    def test_post_serialize_meta_not_authenticated(self):
        post = Post.objects.get(id=1)
        actual = post.serialize(AnonymousUser())["meta"]
        expected = {
            "authenticated": False
        }
        self.assertEqual(actual, expected)

    def test_post_serialize_meta_owned(self):
        post = Post.objects.get(id=1)
        user = post.author
        actual = post.serialize(user)["meta"]
        expected = {
           "authenticated": True,
           "owned": True,
           "liked": False
        }
        self.assertEqual(actual, expected)
'''
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
        '''

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
            "posts": {
                {
                    "id": 1
                    "author": {
                        "id": 1, 
                        "username": "user1"
                    },
                    "content": "post11", 
                    ""}}}'''

    
      

  


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
        
            
        

