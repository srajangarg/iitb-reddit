from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.utils import timezone
import re
from .models import *
from users.models import Subscriber, Moderator
from posts.models import *
from posts.views import updatePostFeatures

def index(request, subreddit_title):

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return HttpResponse("Subreddit Does Not Exist")

    num_subscribers = subscribersCount(subreddit)
    moderators = getModerators(subreddit)
    ismoderator = request.user in moderators or request.user.is_staff
    assignedmod = request.user in moderators
    if request.user.is_authenticated():
        subscribed = checkSubscribed(request.user, subreddit)
        posts = feed(subreddit, request.user)
        events = getEvents(subreddit, request.user)
    else:
        posts = feed(subreddit)
        events = getEvents(subreddit)
        subscribed = False
    return render(request, "subreddit.html", {"subreddit" : subreddit, "posts" : posts, 
                                              "num_subscribers" : num_subscribers, "subscribed" : subscribed,
                                              "moderators" : moderators, "ismoderator" : ismoderator,
                                              "assignedmod" : assignedmod, "events" : events})


def popularSubreddits(num=5, user = None):

    subreddits = list(Subreddit.objects.all())
    if(user != None):
        subreddits = [subreddit for subreddit in subreddits if not checkSubscribed(user,subreddit)]
    return sorted(subreddits, key = lambda s: subscribersCount(s), reverse=True)[:num]


def feed(subreddit, user = None):

    posts = []

    for p in LinkPost.objects.filter(posted_in = subreddit).extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(posted_in = subreddit).extra(select = {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))

    return sorted(posts, key = lambda p: p.num_votes, reverse=True)

def getEvents(subreddit, user=None):
    
    events = []

    for e in Event.objects.filter(posted_in=subreddit):
        if timezone.now() > e.time:
            events.append(updatePostFeatures(e, user))

    return sorted(events, key=lambda e: e.time, reverse=True)

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

def addSubredditForm(request):
    if request.user.is_authenticated():
        return render(request, "newsubreddit.html")
    else:
        return HttpResponse("Login to post!")

def addSubreddit(request):

    if request.method == 'GET':
        return redirect('index')
    subreddit_title = request.POST['title']
    if not validate_title(subreddit_title):
        return JsonResponse({'success' : False, 'Error' : "Subreddit Title should contain only A-Za-z0-9_"})

    description = request.POST['description']

    if not request.user.is_authenticated() :
        return HttpResponse("Login to add a new subreddit!")

    # some conditions for allowing to make a new subreddit

    if Subreddit.objects.filter(title=subreddit_title).exists():
        return JsonResponse({'success' : False, 'Error' : "Subreddit Already Exists"})

    subreddit = Subreddit(title=subreddit_title, description=description)
    subreddit.save()

    mod = Moderator(redditer=request.user, subreddit=subreddit)
    mod.save()

    return JsonResponse({'success' : True, 'Message' : "Added Subreddit"})

def subscribe(request):

    if request.method == 'GET':
        return redirect('index')

    subreddit_title = request.POST['subreddit']

    if not request.user.is_authenticated():
        return HttpResponse("Login to subscribe!")

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return JsonResponse({'success' : False, 'Error' : "Subreddit Does not exist"})

    qs = Subscriber.objects.filter(redditer = request.user, subreddit=subreddit)

    if qs.count() == 0:
        subs = Subscriber(redditer=request.user, subreddit=subreddit)
        subs.save()

    return JsonResponse({'success' : True})


def unsubscribe(request):

    if request.method == 'GET':
        return redirect('index')
    subreddit_title = request.POST['subreddit']
    if not request.user.is_authenticated():
        return JsonResponse({'success' : False, 'Error' : "Login to subscribe!"})

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return JsonResponse({'success' : False, 'Error' : "Subreddit Does not exist"})

    qs = Subscriber.objects.filter(redditer = request.user, subreddit=subreddit)

    if qs.count() > 0:
        qs.delete()

    return JsonResponse({'success' : True})

def addModerator(request):
    if request.method == 'GET':
        return redirect('index')

    subreddit_title = request.POST['subreddit']
    newmod_username = request.POST['username']

    try:
        newmod = get_user_model().objects.get(username=newmod_username)
    except:
        return JsonResponse({'success' : False, 'Error' : "User does not exist"})

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return JsonResponse({'success' : False, 'Error' : "Subreddit Does not exist"})

    moderators = getModerators(subreddit)

    if not request.user.is_authenticated():
        return JsonResponse({'success' : False, 'Error' : "Login to add!"})
    elif not request.user in moderators and not request.user.is_staff:
        return JsonResponse({'success' : False, 'Error' : "Only current mods can add a new mod!"})
    elif newmod in moderators:
        return JsonResponse({'success' : False, 'Error' : "Already a mod!"})

    m = Moderator(redditer=newmod, subreddit=subreddit)
    m.save()

    return JsonResponse({'success' : True})

def delModerator(request):
    if request.method == 'GET':
        return redirect('index')

    subreddit_title = request.POST['subreddit']

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return JsonResponse({'success' : False, 'Error' : "Subreddit Does not exist"})

    moderators = getModerators(subreddit)

    if not request.user.is_authenticated():
        return JsonResponse({'success' : False, 'Error' : "Login to add!"})
    elif not request.user in moderators:
        return JsonResponse({'success' : False, 'Error' : "Not a Mod!"})

    qs = Moderator.objects.get(redditer=request.user, subreddit=subreddit)
    qs.delete()

    if len(moderators) == 1:
        assignNewModerator(subreddit)

    return JsonResponse({'success' : True})

def assignNewModerator(subreddit):
# TODO by garg
    return

def validate_title(username):
    return re.compile('[A-Za-z0-9_]+$').match(username)