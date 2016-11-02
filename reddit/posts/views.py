from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from subreddits.models import Subreddit
from posts.models import TextPost, LinkPost

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