from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import *
from subreddits.models import Subreddit
from posts.models import TextPost, LinkPost, Comment, Vote
from posts.views import updatePostFeatures
import calendar, ldap
from datetime import datetime, timedelta
from math import log
import re 
# make this date timezone aware
epoch = timezone.make_aware(datetime(1970, 1, 1), timezone.get_current_timezone())

def epoch_seconds(date):
    td = date - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

# To calculate the score of a post for the hot ranking algorithm
def hot(num_votes, date):
    order = log(max(abs(num_votes), 1), 10)
    sign = 1 if num_votes > 0 else -1 if num_votes < 0 else 0
    seconds = epoch_seconds(date) - 1134028003
    return round(  (order * sign) + (seconds / 45000),   7)


def index(request, ranking = ""):
    # print ranking
    if request.user.is_authenticated():
        posts = feed(ranking,request.user)
    else:
        posts = feed(ranking)
    return render(request, "index.html", {"posts" : posts})

top_sort_orders = ['','hour','day','month','year','all']

def top(request, sort_type):
    if(sort_type in top_sort_orders):
        if(request.user.is_authenticated):
            posts = top_feed(sort_type,request.user)
        else:
            posts = top_feed(sort_type)

        return render(request,"index.html",{"posts" : posts})
    else:
        # TODO : redirect to some page saying lost!
        print("lost")

def login(request):

    if request.method == 'GET':
        return redirect('index')
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        auth_login(request, user)
        return JsonResponse({'success' : True})

    else:
        return JsonResponse({'success' : False, 'Error' : "Invalid credentials"})


def ldap_auth(email, password):

    if not email.endswith("@iitb.ac.in"):
        return False

    username = "uid=" + email[:email.find("@")]

    conn = ldap.initialize('ldap://ldap.iitb.ac.in')
    search_result = conn.search_s('dc=iitb,dc=ac,dc=in', ldap.SCOPE_SUBTREE, username, ['uid','employeeNumber'])

    try:
        if search_result:
            authenticate = conn.bind_s(search_result[0][0], password)
            return True
        else:
            return False
    except:
        return False

def signup(request):

    if request.method == 'GET':
        return redirect('index')

    email = request.POST['email']
    ldappass = request.POST['ldappass']
    username = request.POST['username']
    password = request.POST['password']

    if ldap_auth(email, ldappass):
        if get_user_model().objects.filter(email=email).exists():
            return JsonResponse({'success' : False, 'Error' : "LDAP already in use"})
        
        username = username.strip()
        if not validate_username(username):
            return JsonResponse({'success' : False, 'Error' : "Username should contain only a-z0-9_"})
        if get_user_model().objects.filter(username=username).exists():
            return JsonResponse({'success' : False, 'Error' : "Username already taken up"})

        user = get_user_model().objects.create_user(username, email, password)

        if user is not None:
            login_user = authenticate(username=username, password=password)
            auth_login(request, login_user)
            return JsonResponse({'success' : True})

    return JsonResponse({'success' : False, 'Error' : "Invalid LDAP credentials"})

def logout(request):

    auth_logout(request)
    return redirect('index')

def user(request, username):
    try:
        view_user = get_user_model().objects.get(username = username)
    except:
        return HttpResponse("User Does Not Exist")
    
    moderated_subreddit = moderatedSubreddit(username)
    ismoderator = len(moderated_subreddit) > 0
    if request.user.is_authenticated():
        userposts = userPosts(username, request.user)
        mypage = request.user == view_user
    else:
        userposts = userPosts(username)
    return render(request, "user.html", {"posts" : userposts, "username" : username, 
                                         "moderates" : moderated_subreddit, "mypage" : mypage, 
                                         "ismoderator" : ismoderator})
    

def userUpvoted(request, username):
    try:
        view_user = get_user_model().objects.get(username = username)
    except:
        return HttpResponse("User Does Not Exist")
    
    moderated_subreddit = moderatedSubreddit(username)
    ismoderator = len(moderated_subreddit) > 0
    if request.user.is_authenticated():
        userposts = userVotedPosts(username, 1, request.user)
        mypage = request.user == view_user
    else:
        userposts = userVotedPosts(username, 1)
    return render(request, "user.html", {"posts" : userposts, "username" : username, 
                                         "moderates" : moderated_subreddit, "mypage" : mypage, 
                                         "ismoderator" : ismoderator})

def userDownvoted(request, username):
    try:
        view_user = get_user_model().objects.get(username = username)
    except:
        return HttpResponse("User Does Not Exist")
    
    moderated_subreddit = moderatedSubreddit(username)
    ismoderator = len(moderated_subreddit) > 0
    if request.user.is_authenticated():
        userposts = userVotedPosts(username, -1, request.user)
        mypage = request.user == view_user
    else:
        userposts = userVotedPosts(username, -1)
    return render(request, "user.html", {"posts" : userposts, "username" : username, 
                                         "moderates" : moderated_subreddit, "mypage" : mypage, 
                                         "ismoderator" : ismoderator})

# def myaccount(request):
#
#     if request.user.is_authenticated():
#         user_email = request.user.email
#         return redirect('user/' + user_email)
#     else:
#         return redirect('index')

def votedByUser(post, user, vote):
    qs = Vote.objects.filter(voted_on__id = post.id, voted_by__username = user)
    return len(qs) > 0 and int(qs[0].value) == vote

def allPosts(user):

    posts = []

    for p in LinkPost.objects.extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.extra(select = {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))

    return posts

def feed(ranking="", user = None):

    posts = allPosts(user)

    if(ranking == "" or ranking == "hot"):
        return sorted(posts, key = lambda post : hot(post.num_votes, post.created_on),reverse=True)
    elif(ranking == "new"):
        return sorted(posts, key = lambda p: p.created_on, reverse=True)

def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, calendar.monthrange(y, m)[1])
    return date.replace(day=d,month=m, year=y)

def top_feed(sort_type,user = None):

    print(sort_type)
    time_to_compare = datetime.now() #datetime.now()
    time_to_compare = timezone.make_aware(time_to_compare, timezone.get_current_timezone())
    if(sort_type == 'hour'):
        time_to_compare -= timedelta(hours = 1)
    elif(sort_type == 'day'):
        time_to_compare -= timedelta(days = 1)
    elif(sort_type == 'month'):
        time_to_compare = monthdelta(time_to_compare, -1)
    elif(sort_type == 'year'):
        time_to_compare = monthdelta(time_to_compare, -12)
    elif(sort_type == 'all' or sort_type == ""):
        time_to_compare = epoch

    posts = []

    for p in LinkPost.objects.filter(created_on__gte=time_to_compare).\
        extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(created_on__gte=time_to_compare).extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))
    return sorted(posts, key=lambda p: p.num_votes, reverse=True)

def userPosts(username, user = None):

    posts = []

    for p in LinkPost.objects.filter(posted_by__username=username).extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(posted_by__username=username).extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))

    return sorted(posts, key = lambda p: p.created_on, reverse=True)

def userVotedPosts(username, vote, user = None):

    posts = allPosts(user)
    posts = [p for p in posts if votedByUser(p, username, vote)]

    return sorted(posts, key = lambda p: p.created_on, reverse=True)

def moderatedSubreddit(username):

    qs = Moderator.objects.filter(redditer__username=username)
    subrs = []
    for r in qs:
        subrs.append(r.subreddit)
    return subrs

def validate_username(username):
    return re.compile('[a-z0-9_]+$').match(username)