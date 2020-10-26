import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import User, Post


def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, "network/index.html", {
        "page_obj": page_obj
    })

def user_page(request, username):
    target_user = User.objects.get(username=username)
    posts = Post.objects.filter(user__username=username).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, "network/user.html", {
        "target_user": target_user,
        "page_obj": page_obj
    })

@login_required
def following(request):
    all_posts = Post.objects.order_by("-timestamp").all()

    posts = []
    # get all followed users after log in
    for post in all_posts:
        # add to the users posts list, followed by the logged user
        if post.user in request.user.following.all():
            posts.append(post)

    paginator = Paginator(posts, 10)

    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })

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

@csrf_exempt
@login_required
def new(request):
    if request.method != "POST":
        # must be a  POST method to create a post
        return JsonResponse({"error": "Must be POST method"}, status=400)

    data = json.loads(request.body)

    if not data.get("content", ""):
        #must have content
        return JsonResponse({"error": "The post must have content"}, status=400)

    #create and save post
    post = Post(
        user=User.objects.get(pk=request.user.id),
        content=data.get("content", "")
    )

    post.save()

    return JsonResponse({"message": "Success, post published!"}, status=200)

@csrf_exempt
def follow(request, username):
    target_user = User.objects.get(username=username)

    if request.user in target_user.followers.all():
        #means unfollow
        target_user.followers.remove(request.user)
        target_user.save()

        return JsonResponse({"message": f'{username} unfollowed!'})

    target_user.followers.add(request.user)
    target_user.save()

    return JsonResponse({"message": f'{username} followed!'})

@csrf_exempt
@login_required
def edit(request):
    if request.method != "PUT":
        #must be a PUT method to create a post
        return JsonResponse({"error": "Must be PUT method"}, status=400)

    data = json.loads(request.body)

    post_id = data.get("postId", "")
    content = data.get("content", "")

    post = Post.objects.get(pk=post_id)

    if request.user.username != post.user.username:
        #means another user is trying to edit
        return JsonResponse({"error": "Can't edit another user's post"}, status=403)

    #change content
    post.content = content
    post.save()

    return JsonResponse({"message": "Post edited!"}, status=200)

@csrf_exempt
@login_required
def like(request):
    if request.method != "PUT":
        #must be a  PUT method to create a post
        return JsonResponse({"error": "Must be PUT method"}, status=400)

    data = json.loads(request.body)

    post_id = data.get("postId", "")

    post = Post.objects.get(pk=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        post.save()

        return JsonResponse({"liked": False}, status=200)

    post.likes.add(request.user)
    post.save()

    return JsonResponse({"liked": True}, status=200)
