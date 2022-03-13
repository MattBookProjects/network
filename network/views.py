import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.middleware.csrf import get_token

from .models import User, Post, Follow

#LOGIN_URL = reverse('login')

def csrf(request):
    return JsonResponse({"token": get_token(request)})


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
        try:
            data = json.loads(request.body)
            try:
                content = data.get("content")
            except:
                return JsonResponse({"message": "Missing content parameter"}, status=400)
            Post.objects.create(author=request.user, content=content)
            return JsonResponse({"message": "Post created successfully"}, status=201)
        except:
            return HttpResponse(status=500)
    else:
        return JsonResponse({"message": "POST method required"}, status=400)

@login_required(login_url="/login/")
def posts(request, id):
    try:
        post = Post.objects.get(id=id)
    except:
        return JsonResponse({"message": "Post not found"}, status=404)
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"message": "Missing request body"}, status=400)
        mode = data.get("mode")
        if mode is None:
            return JsonResponse({"message": "Missing mode parameter"}, status=400)
        if mode == "like":
            like = data.get("like")
            if like is None:
                return JsonResponse({"message": "Missing like parameter"}, status=400)
            if like == True:
                if post.likes.filter(id = request.user.id).count() > 0:
                    return JsonResponse({"message": "You already like this post"}, status=409)
                post.likes.add(request.user)
                return HttpResponse(status=204)
            if like == False: 
                if post.likes.filter(id = request.user.id).count() == 0:
                    return JsonResponse({"message": "You already don't like this post"}, status=409)
                post.likes.remove(request.user)
                return HttpResponse(status=204)
            return JsonResponse({"message": "Invalid like parameter"}, status=400)            
        if mode == "edit":
            if post.author != request.user:
                return JsonResponse({"message": "You can only edit your own posts"}, status=403)
            content = data.get('content')
            if content is None:
                return JsonResponse({"message": "Missing content parameter"}, status=400)
            post.content = content
            post.save()
            return HttpResponse(status=204)
        return JsonResponse({"message": "Invalid mode parameter"}, status=400)   
    return JsonResponse({"message": "PUT method required"}, status=400)

def profiles(request, id):
    try:
        user = User.objects.get(id=id)
    except:
        return JsonResponse({"message": "Profile not found"}, status=404)
    try:
        if request.method == "GET":
            return JsonResponse(user.serialize(request.user), safe=False, status=200)
        if request.method == "PUT":
            try:
                data = json.loads(request.body)
            except:
                return JsonResponse({"message": "Missing request body"}, status=400)
            follow = data.get("follow")
            if follow is None:
                return JsonResponse({"message": "Missing follow parameter"},status=400)
            if follow == True:
                if user.followers.filter(follower=request.user).count() > 0:
                    return JsonResponse({"message": "You already follow this user"}, status=409)
                Follow.objects.create(follower=request.user, followed=user)
                return HttpResponse(status=204)        
            if follow == False:
                if user.followers.filter(follower=request.user).count() == 0:
                    return JsonResponse({"message": "You already don't follow this user"}, status=409)
                Follow.objects.get(follower=request.user, followed=user).delete()
                return HttpResponse(status=204)
            return JsonResponse({"message": "Invalid follow parameter"}, status=400)
        return JsonResponse({"message": "Invalid request method"}, status=400)
    except:
        return HttpResponse(status=500)
    

def all_posts(request):
    posts = Post.objects.all().order_by("-date")
    #return JsonResponse([post.toJson(request.user) for post in posts], safe=False)
    #return JsonResponse({"post" : {"author": "author", "content": "content"}}, safe=False)
    return JsonResponse([post.serialize(request.user) for post in posts], safe=False)
    
@login_required(login_url="/login/")
def following_posts(request):
    posts = Post.objects.filter(author__in=User.objects.filter(followers__in=Follow.objects.filter(follower=request.user))).order_by("-date")
    return JsonResponse([post.serialize(request.user) for post in posts], safe=False)



  
            

        