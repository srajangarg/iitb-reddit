from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.db.models import Sum
from subreddits.models import Subreddit
from .models import *
from datetime import timedelta
from django.utils import timezone

def numComments(post):
    
    num = 0
    qs = Comment.objects.filter(commented_on = post)
    num += qs.count()
    for c in qs:
        num += numComments(c)
    return num

def updatePostFeatures(post, user=None):

    post.num_votes = Vote.objects.filter(voted_on__id = post.id).aggregate(votes = Sum('value')).get('votes')
    
    post.num_comments = numComments(post)

    if post.num_votes == None:
        post.num_votes = 0

    if user is not None:
        
        qs = Vote.objects.filter(voted_on__id = post.id, voted_by = user)
        if len(qs) > 0:
            post.vote = qs[0].value

    return post

# def getComments(post):

#     comments = []

#     for c in Comment.objects.filter(commented_on = post).extra(select={'childs' : 0}):
#         c.childs = getComments(c)
#         comments.append(c)

#     return comments


def getComments(post, depth, user=None):

    comments = []

    for c in Comment.objects.filter(commented_on = post).order_by('-created_on').extra(select={'depth' : 0, 'child' : 0, 'childrange' : 0, 'num_votes' : 0, 'num_comments' : 0, 'vote' : 0}):
        updated_c = updatePostFeatures(c, user)
        updated_c.depth = depth
        comments.append(updated_c)
        comments += getComments(updated_c, depth + 1, user)

    d = 0
    for c in comments:
        c.child = c.depth - d
        d = c.depth
        if c.child < 0:
            c.childrange = range(-c.child)
    return comments 


# def printComments(comments, string = ""):

#     for c in comments:
#         print string + str(c.id)
#         printComments(c.childs, "    ")

def post(request, post_id):

    qs = TextPost.objects.filter(id = post_id)
    if qs.count() == 1:
        qs = qs.extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params=('text',))
        p = qs.get()
    else:
        qs = LinkPost.objects.filter(id = post_id)
        print qs.count()
        if qs.count() == 1:
            qs = qs.extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params=('link',))
            p = qs.get()
        else:
            return HttpResponse("No such post!")

    if request.user.is_authenticated(): 
        updatePostFeatures(p,request.user)
        comments = getComments(p, 0, request.user)
    else:
        updatePostFeatures(p)
        comments = getComments(p, 0)

    archived = False
    if (timezone.now() > p.expires_on):
        archived = True
    return render(request, "post.html", {"post" : p, "comments" : comments, "archived" : archived})

def newPost(request):

    if request.user.is_authenticated():
        subreddits = [str(s.title) for s in Subreddit.objects.all()]
        selected_subreddit = request.GET.get('subreddit', "")
        return render(request, "newpost.html", {"subreddits" : subreddits, "selected_subreddit" : selected_subreddit})
    else:
        return HttpResponse("Login to post!")

def submitPost(request):

    if request.method == 'GET':
        return redirect('index')
    title = request.POST['title']
    subreddit_title = request.POST['subreddit']
    post_type = request.POST['type']

    if not request.user.is_authenticated():
        return JsonResponse({'success' : False, 'Error' : "Login to post!"})

    try:
        subreddit = Subreddit.objects.get(title=subreddit_title)
    except:
        return JsonResponse({'success' : False, 'Error' : "Subreddit does not exist!"})

    if post_type == 'text':
        text = request.POST['text']
        p = TextPost(posted_by = request.user, posted_in=subreddit, title=title, text=text)
        p.save()
    else:
        link = request.POST['url']
        p = LinkPost(posted_by = request.user, posted_in=subreddit, title=title, link=link)

    if request.POST.getlist('timed[]'):
        print request.POST['days'], request.POST['hours']
        p.expires_on = timezone.now() + timedelta(days=int(request.POST['days']), 
                                                  hours=int(request.POST['hours']))  
    p.save()
    return JsonResponse({'success' : True, 'Message' : "Posted"})

def vote(request):

    if request.method == 'GET':
        return redirect('index')

    if request.user.is_authenticated():
        post_id = request.POST['postId']
        action = request.POST['action']
        status = request.POST['status']
        qs = Vote.objects.filter(voted_on__id = post_id, voted_by = request.user)

        if len(qs) == 0 and status != action:
            p = Post.objects.get(id = post_id)
            v = Vote(value = action, voted_on = p, voted_by = request.user)
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
        return JsonResponse({'success' : True, 'vote' : updated})            
    else:
        return JsonResponse({'success' : False})   

def submitComment(request):

    if request.method == 'GET':
        return redirect('index')
    
    if request.user.is_authenticated():
        comment_on_id = request.POST['comment_on']
        reply = request.POST['reply']
        p = Post.objects.get(id = comment_on_id)
        c = Comment(posted_by = request.user, text = reply, commented_on = p)
        c.save()
        return JsonResponse({'success' : True})
    return JsonResponse({'success' : False, 'Error' : "Login to reply"})

def deletePost(request):
    return JsonResponse({'success' : False})