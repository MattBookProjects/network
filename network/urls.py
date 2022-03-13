
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("posts/<int:id>", views.posts, name="posts"),
    path("posts", views.all_posts, name="all_posts"),
    path("posts/following", views.following_posts, name="following_posts"),
    path("profiles/<int:id>", views.profiles, name="profiles"),
    path("csrf", views.csrf, name="csrf"),
]
