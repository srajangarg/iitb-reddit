from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.db.models import Sum
from subreddits.models import Subreddit
from posts.models import TextPost, LinkPost, Comment, Vote

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

def feed():
    posts = []
    for p in LinkPost.objects.extra(select={'num_votes' : 0, 'num_comments' : 0}):
        p.num_votes = Vote.objects.filter(voted_on = p).aggregate(votes = Sum('value')).get('votes')
        p.num_comments = Comment.objects.filter(commented_on = p).count()
        if p.num_votes == None:
            p.num_votes = 0
        posts.append(p)
    for p in TextPost.objects.extra(select={'num_votes' : 0, 'num_comments' : 0}):
        p.num_votes = Vote.objects.filter(voted_on = p).aggregate(votes=Sum('value')).get('votes')
        p.num_comments = Comment.objects.filter(commented_on = p).count()
        if p.num_votes == None:
            p.num_votes = 0
        posts.append(p)
    return posts