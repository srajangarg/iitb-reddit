from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.db.models import Sum
from subreddits.models import Subreddit
from posts.models import TextPost, LinkPost, Comment, Vote

def index(request):
    if request.user.is_authenticated():
        posts = feed(request.user)
    else:
        posts = feed()
    return render(request, "index.html", {"posts" : posts})

def login(request):

    if request.method == 'GET':
        return redirect('index')
    email = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
        auth_login(request, user)
        return redirect('index')
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
    if request.user.is_authenticated():
        userposts = userfeed(username)
    else:
        userposts = userfeed(username, request.user)
    return render(request, "user.html", {"posts" : userposts})

# def myaccount(request):
# 
#     if request.user.is_authenticated():
#         user_email = request.user.email
#         return redirect('user/' + user_email)
#     else:
#         return redirect('index')

def updatePostFeatures(p, user):

    p.num_votes = Vote.objects.filter(voted_on = p).aggregate(votes = Sum('value')).get('votes')
    p.num_comments = Comment.objects.filter(commented_on = p).count()

    if p.num_votes == None:
        p.num_votes = 0

    if user is not None:
        qs = Vote.objects.filter(voted_on = p, voted_by = user)
        if len(qs) > 0:
            p.vote = qs[0].value
    return p

def feed(user = None):
    posts = []
    for p in LinkPost.objects.extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))
    for p in TextPost.objects.extra(select = {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s'}, 
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))
    return posts


def userfeed(username, user = None):

    posts = []
    for p in LinkPost.objects.filter(posted_by__email = username).extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s'}, 
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))
    for p in TextPost.objects.filter(posted_by__email = username).extra(select = {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s'}, 
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))
    return posts 