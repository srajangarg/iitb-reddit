from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.db.models import Sum
from subreddits.models import Subreddit
from subreddits.views import getModerators, updatePostFeatures, numComments
from .models import *
from datetime import timedelta
from django.utils import timezone
import opengraph

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

def post(request, post_id):

    qs = TextPost.objects.filter(id = post_id)
    if qs.count() == 1:
        qs = qs.extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params=('text',))
        p = qs.get()
    else:
        qs = LinkPost.objects.filter(id = post_id)
        if qs.count() == 1:
            qs = qs.extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params=('link',))
            p = qs.get()
        else:
            qs = Event.objects.filter(id = post_id)
            if qs.count() == 1:
                qs = qs.extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                        select_params=('event',))
                p = qs.get()
            else:
                return HttpResponse("No such post!")

    if request.user.is_authenticated(): 
        updatePostFeatures(p,request.user)
        comments = getComments(p, 0, request.user)
        ismoderator = request.user in getModerators(p.posted_in) or request.user.is_staff or p.posted_by == request.user
    else:
        updatePostFeatures(p)
        comments = getComments(p, 0)
        ismoderator = False

    archived = False
    if (timezone.now() > p.expires_on):
        archived = True
    return render(request, "post.html", {"post" : p, "comments" : comments, "archived" : archived, "ismoderator" : ismoderator})

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
        if request.POST.getlist('timed[]'):
            p.expires_on = timezone.now() + timedelta(days=int(request.POST['days']), 
                                                  hours=int(request.POST['hours']))
        else:
            p.expires_on = timezone.now() + timedelta(days=150)
    
    elif post_type == 'link':

        link = request.POST['url']
        p = LinkPost(posted_by = request.user, posted_in=subreddit, title=title, link=link)
        if request.POST.getlist('timed[]'):
            p.expires_on = timezone.now() + timedelta(days=int(request.POST['days']), 
                                                  hours=int(request.POST['hours']))
        else:
            p.expires_on = timezone.now() + timedelta(days=150)

        try:
            metadata = opengraph.OpenGraph(url=link)
            p.imgurl = metadata["image"]
            p.site = metadata["site_name"]
        except:
            pass
    
    elif post_type == 'event':

        venue = request.POST['venue']
        time = request.POST['time']
        print time
        description = request.POST['description']
        p = Event(posted_by = request.user, posted_in=subreddit, title=title, time=time, venue=venue, description=description)
        p.expires_on = time

    p.save()
    return JsonResponse({'success' : True, 'Message' : "Posted", 'postId' : p.id})

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
        if not Post.objects.filter(id=comment_on_id).exists():
            return JsonResponse({'success' : False, 'Error' : "No such post exists"})
            
        p = Post.objects.get(id = comment_on_id)
        c = Comment(posted_by = request.user, text = reply, commented_on = p)
        c.save()
        return JsonResponse({'success' : True})
    return JsonResponse({'success' : False, 'Error' : "Login to reply"})

def deletePost(request):

    if request.method == 'GET':
        return redirect('index')
    
    if request.user.is_authenticated():
        postId = request.POST['postId']
        if not Post.objects.filter(id=postId).exists():
            return JsonResponse({'success' : False, 'Error' : "No such post exists"})
        
        qs = Post.objects.filter(id=postId)
        if qs[0].deleted:
            return JsonResponse({'success' : False, 'Error' : "Already deleted"})
            
        
        qs2 = TextPost.objects.filter(id=postId)
        if qs2.exists():
            qs2.update(title="[deleted]", text="[deleted]")
            qs2.update(expires_on=timezone.now(), deleted=True)

        qs2 = LinkPost.objects.filter(id=postId)
        if qs2.exists():
            qs2.update(title="[deleted]", link="")
            qs2.update(expires_on=timezone.now(), deleted=True)

        qs2 = Event.objects.filter(id=postId)
        if qs2.exists():
            qs2.update(title=qs2[0].title + " [cancelled]")
            qs2.update(expires_on=timezone.now(), deleted=True)

        qs2 = Comment.objects.filter(id=postId)
        if qs2.exists():
            qs2.update(text="[deleted]", deleted=True)

        return JsonResponse({'success' : True})
    return JsonResponse({'success' : False, 'Error' : "Login to delete"})