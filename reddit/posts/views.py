from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.db.models import Sum
from subreddits.models import Subreddit
from .models import *
import json

def numComments(post):
    
    num = 0
    qs = Comment.objects.filter(commented_on = post)
    num += qs.count()
    for c in qs:
        num += numComments(c)
    return num
    
def updatePostFeatures(post, user):

    post.num_votes = Vote.objects.filter(voted_on = post).aggregate(votes = Sum('value')).get('votes')
    
    post.num_comments = numComments(post)

    if post.num_votes == None:
        post.num_votes = 0

    if user is not None:
        qs = Vote.objects.filter(voted_on = post, voted_by = user)
        if len(qs) > 0:
            post.vote = qs[0].value
    return post

def getComments(post):

    comments = []

    for c in Comment.objects.filter(commented_on = post).extra(select={'childs' : 0}):
        c.childs = getComments(c)
        comments.append(c)

    return comments

# def printComments(comments, string = ""):

#     for c in comments:
#         print string + str(c.id)
#         printComments(c.childs, "    ")

def post(request, post_id):

    p = Post.objects.get(id = post_id)
    comments = getComments(p)
    return render(request, "post.html", {'post' : p, 'comments' : comments})

def newpost(request):

    if request.user.is_authenticated():
        return render(request, "newpost.html")
    else:
        return HttpResponse("Login to post!")

def submitpost(request):

    title = request.POST['title']
    subreddit_title = request.POST['subreddit']
    post_type = request.POST['type']

    if not request.user.is_authenticated():
        return HttpResponse("Login to post!")

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return HttpResponse("Subreddit Does Not Exist")

    if post_type == 'text':
        text = request.POST['text']
        p = TextPost(posted_by = request.user, posted_in=subreddit, title=title, text=text)
        p.save()
    else:
        link = request.POST['url']
        p = LinkPost(posted_by = request.user, posted_in=subreddit, title=title, link=link)
        p.save()
    return HttpResponse("Posted")

def vote(request):

    if request.user.is_authenticated():
        user = request.user
        post_id = request.POST['postId']
        action = request.POST['action']
        status = request.POST['status']
        qs = Vote.objects.filter(voted_on__id = post_id, voted_by = user)

        if len(qs) == 0 and status != action:
            p = Post.objects.get(id = post_id)
            v = Vote(value = action, voted_on = p, voted_by = user)
            v.save()
            updated = action
        elif len(qs) > 0 and status == action:
            # TODO error handling
            qs.delete()
            updated = 0
        elif len(qs) > 0 and status != action:
            qs.update(value = action)
            updated = action
        else:
            updated = 0
        return HttpResponse(json.dumps({'success' : True, 'vote' : updated}), content_type="application/json")             
    else:
        return HttpResponse(json.dumps({'success' : False}), content_type="application/json")     
