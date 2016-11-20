from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .models import *
from posts.models import TextPost, LinkPost, Comment, Vote
from posts.views import updatePostFeatures

def index(request, subreddit_title):
    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return HttpResponse("Subreddit Does Not Exist")

    if request.user.is_authenticated():
        posts = feed(subreddit, request.user)
    else:
        posts = feed(subreddit)
    return render(request, "index.html", {"subreddit" : subreddit, "posts" : posts})


def feed(subreddit, user = None):

    posts = []

    for p in LinkPost.objects.filter(posted_in = subreddit).extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(posted_in = subreddit).extra(select = {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))

    return sorted(posts, key = lambda p: p.num_votes, reverse=True)