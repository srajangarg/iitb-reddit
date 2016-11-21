from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .models import *
from users.models import Subscriber, Moderator
from posts.models import TextPost, LinkPost, Comment, Vote
from posts.views import updatePostFeatures

def index(request, subreddit_title):

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return HttpResponse("Subreddit Does Not Exist")

    num_subscribers = subscribersCount(subreddit)
    
    if request.user.is_authenticated():
        posts = feed(subreddit, request.user)
    else:
        posts = feed(subreddit)
    return render(request, "subreddit.html", {"subreddit" : subreddit, "posts" : posts, "num_subscribers" : num_subscribers})


def feed(subreddit, user = None):

    posts = []

    for p in LinkPost.objects.filter(posted_in = subreddit).extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(posted_in = subreddit).extra(select = {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))

    return sorted(posts, key = lambda p: p.num_votes, reverse=True)

def subscribersCount(subreddit):
    return Subscriber.objects.filter(subreddit=subreddit).count()

# def moderators(subreddit):

def addSubreddit(request):

    if request.method == 'GET':
        return redirect('index')
    subreddit_title = request.POST['subreddit']
    description = request.POST['description']

    if not request.user.is_authenticated() :
        return HttpResponse("Login to add a new subreddit!")
    
    # some conditions for allowing to make a new subreddit

    if Subreddit.objects.filter(title=subreddit_title).exists():
        return HttpResponse("Subreddit Already Exists")

    subreddit = Subreddit(title=subreddit_title, description=description)
    subreddit.save()

    mod = Moderator(redditer=request.user, subreddit=subreddit)
    mod.save()

    subs = Subscriber(redditer=request.user, subreddit=subreddit)
    subs.save()

    return HttpResponse("Added Subreddit")

def subscribe(request):

    if request.method == 'GET':
        return redirect('index')
    subreddit = request.POST['subreddit']
    if not request.user.is_authenticated():
        return HttpResponse("Login to subscribe!")

    qs = Subscriber.objects.filter(redditer = request.user, subreddit=subreddit)
    
    if qs.count() == 0:
        subs = Subscriber(redditer=request.user, subreddit=subreddit)
        subs.save()

    return HttpResponse(json.dumps({'success' : True}), content_type="application/json")


def unsubscribe(request):

    if request.method == 'GET':
        return redirect('index')
    subreddit = request.POST['subreddit']
    if not request.user.is_authenticated():
        return HttpResponse("Login to subscribe!")

    qs = Subscriber.objects.filter(redditer = request.user, subreddit=subreddit)
    
    if qs.count() > 0:
        qs.delete()

    return HttpResponse(json.dumps({'success' : True}), content_type="application/json")