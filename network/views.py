import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def post(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content")
        post = Post(creator=request.user, content=content)
        post.save()
        return JsonResponse({"message": "Posted successfully"}, status=201)

def posts(request, id):
    if request.method == "PUT":
        data = json.loads(request.body)
        like = data.get("like")
        try:
            post = Post.objects.get(id=id)
            if like:
                post.likers.add(request.user)
            else:
                post.likers.remove(request.user)
            return JsonResponse({"message": "Post updated successfully"}, status=204)
        except IntegrityError:
            return JsonResponse({"message": "Post not found"}, status=404)
     
    else:
        return JsonResponse({"message": "Put method required"}, status=405)

def profiles(request, id):
    try:
        user = User.objects.get(id=id)
        if request.method == "GET":
            return JsonResponse(user.serialize(), safe=False)
        elif request.method == "PUT":
            data = json.loads(request.body)
            follow = data.get("follow")
            if follow:
                request.user.following.add(user)
            else:
                request.user.following.remove(user)
            return JsonResponse({"message": "Profile updated successfully"}, status=204)
    except IntegrityError:
        return JsonResponse({"message": "User not found"}, status=404)

def all_posts(request):
    posts = Post.objects.all().order_by("-date")
    return JsonResponse([post.serialize() for post in posts], safe=False)

def following_posts(request):
    posts = Post.objects.filter(author=request.user.following).order_by("-date")
    return JsonResponse([post.serialize() for post in posts], safe=False)

  
            

        