from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from subreddits.models import Subreddit
from posts.models import TextPost, LinkPost
import json
from django.core.serializers.json import DjangoJSONEncoder

def index(request):

    posts = feed()
    return render(request, "index.html", {"username" : request.user, "posts" : posts})

def login(request):

    if request.method == 'GET':
        return redirect('index')
    email = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
        auth_login(request, user)
        return render(request, "index.html")
    else:
        return HttpResponse("Invalid credentials")

def signup(request):

    if request.method == 'GET':
        return redirect('index')
    email = request.POST['email']
    password = request.POST['password']

    user = get_user_model().objects.create_user(email, password)
    if user is not None:
        return HttpResponse("Successfully Signed Up!")
    else:
        return HttpResponse("Can't sign Up!")

def logout(request):

    auth_logout(request)
    return redirect('index')

def user(request, username):

    return render(request, "user.html")

# def myaccount(request):
# 
#     if request.user.is_authenticated():
#         user_email = request.user.email
#         return redirect('user/' + user_email)
#     else:
#         return redirect('index')

def post(request, postID):

    return render(request, "post.html")

def newpost(request):

    if request.user.is_authenticated():
        user_email = request.user.email
        return render(request, "newpost.html")
    else:
        return HttpResponse("Login to post!")

def submitpost(request):

    title = request.POST['title']
    subreddit_title = request.POST['subreddit']
    post_type = request.POST['type']
    if not request.user.is_authenticated():
        return HttpResponse("Login to post!")

    subreddit = Subreddit.objects.get(title=subreddit_title)
    
    if post_type == 'text':
        text = request.POST['text']
        p = TextPost(posted_by = request.user, posted_in=subreddit, title=title, text=text)
        p.save()
    else:
        link = request.POST['link']
        p = LinkPost(posted_by = request.user, posted_in=subreddit, title=title, link=link)
        p.save()
    return HttpResponse("Posted")

def feed():

    posts = TextPost.objects.all()
    return posts

# POST
#     postID
#     heading
#     user
#     subreddit
#     timestamp
#     num_comments
#     num_upvotes
