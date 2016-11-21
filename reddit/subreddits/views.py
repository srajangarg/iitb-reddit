from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
import json
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
    moderators = getModerators(subreddit)
    ismoderator = request.user in moderators or request.user.is_staff
    if request.user.is_authenticated():
        subscribed = checkSubscribed(request.user, subreddit)
        posts = feed(subreddit, request.user)
    else:
        posts = feed(subreddit)
        subscribed = False
    return render(request, "subreddit.html", {"subreddit" : subreddit, "posts" : posts, 
                                              "num_subscribers" : num_subscribers, "subscribed" : subscribed, 
                                              "moderators" : moderators, "ismoderator" : ismoderator})


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

def getModerators(subreddit):

    qs = Moderator.objects.filter(subreddit=subreddit)
    mods = []
    for m in qs:
        mods.append(m.redditer)
    return mods

def checkSubscribed(user, subreddit):
    if Subscriber.objects.filter(redditer=user, subreddit=subreddit).exists():
        return True
    else:
        return False


def addSubreddit(request):

    if request.method == 'GET':
        return redirect('index')
    subreddit_title = request.POST['subreddit']
    description = request.POST['description']

    if not request.user.is_authenticated() :
        return HttpResponse("Login to add a new subreddit!")
    
    # some conditions for allowing to make a new subreddit

    if Subreddit.objects.filter(title=subreddit_title).exists():
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Subreddit Already Exists"}), content_type="application/json")

    subreddit = Subreddit(title=subreddit_title, description=description)
    subreddit.save()

    mod = Moderator(redditer=request.user, subreddit=subreddit)
    mod.save()

    return HttpResponse(json.dumps({'success' : True, 'Message' : "Added Subreddit"}), content_type="application/json")

def subscribe(request):

    if request.method == 'GET':
        return redirect('index')

    subreddit_title = request.POST['subreddit']

    if not request.user.is_authenticated():
        return HttpResponse("Login to subscribe!")

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Subreddit Does not exist"}), content_type="application/json")

    qs = Subscriber.objects.filter(redditer = request.user, subreddit=subreddit)
    
    if qs.count() == 0:
        subs = Subscriber(redditer=request.user, subreddit=subreddit)
        subs.save()

    return HttpResponse(json.dumps({'success' : True}), content_type="application/json")


def unsubscribe(request):

    if request.method == 'GET':
        return redirect('index')
    subreddit_title = request.POST['subreddit']
    if not request.user.is_authenticated():
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Login to subscribe!"}), content_type="application/json")

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Subreddit Does not exist"}), content_type="application/json")
    
    qs = Subscriber.objects.filter(redditer = request.user, subreddit=subreddit)
    
    if qs.count() > 0:
        qs.delete()

    return HttpResponse(json.dumps({'success' : True}), content_type="application/json")

def addModerator(request):
    if request.method == 'GET':
        return redirect('index')

    subreddit_title = request.POST['subreddit']
    newmod_username = request.Post['username']

    try:
        newmod = get_user_model().objects.filter(username=newmod_username)
    except:
        return HttpResponse(json.dumps({'success' : False, 'Error' : "User does not exist"}), content_type="application/json")
        
    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Subreddit Does not exist"}), content_type="application/json")
    
    moderators = getModerators(subreddit)
    
    if not request.user.is_authenticated():
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Login to add!"}), content_type="application/json")
    elif not request.user in moderators:
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Only current mods can add a new mod!"}), content_type="application/json")
    elif newmod in moderators:
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Already a mod!"}), content_type="application/json")

    m = Moderator(redditer=newmod, subreddit=subreddit)
    m.save()

    return HttpResponse(json.dumps({'success' : True}), content_type="application/json")

def delModerator(request):
    if request.method == 'GET':
        return redirect('index')

    subreddit_title = request.POST['subreddit']
        
    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Subreddit Does not exist"}), content_type="application/json")
    
    moderators = getModerators(subreddit)
    
    if not request.user.is_authenticated():
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Login to add!"}), content_type="application/json")
    elif not request.user in moderators:
        return HttpResponse(json.dumps({'success' : False, 'Error' : "Not a Mod!"}), content_type="application/json")

    qs = Moderator.objecs.get(redditer=request.user, subreddit=subreddit)
    qs.delete()

    if len(moderators) == 1:
        assignNewModerator(subreddit)

    return HttpResponse(json.dumps({'success' : True}), content_type="application/json")

def assignNewModerator(subreddit):
# TODO by garg
    return    

