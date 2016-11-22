from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import *
from posts.models import *
from subreddits.models import Subreddit
from posts.views import updatePostFeatures
from subreddits.views import  popularSubreddits, checkSubscribed
import calendar, ldap
from datetime import datetime, timedelta
from math import log
import re
# make this date timezone aware
epoch = timezone.make_aware(datetime(2016, 11, 23), timezone.get_current_timezone())

def epoch_seconds(date):
    td = date - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

# To calculate the score of a post for the hot ranking algorithm
def hot(num_votes, date):
    order = log(max(abs(num_votes), 1), 2)
    sign = 1 if num_votes > 0 else -1 if num_votes < 0 else 0
    seconds = epoch_seconds(date)
    return round(  sign * order + (seconds / 45000),   7)

def our_rank(num_votes,posting_time,time_now):
    td = time_now - posting_time
    approx_seconds = td.days * 86400 + td.seconds
    return num_votes + approx_seconds//10000

def index(request, ranking = ""):
    # print ranking
    if request.user.is_authenticated():
        if(ranking == "subscribed"):
            posts = subsribed_feed(request.user)
        else:
            posts = feed(ranking,request.user)
        popularsubreddits = popularSubreddits(user=request.user)
        events = getEvents(request.user)
    else:
        posts = feed(ranking)
        popularsubreddits = popularSubreddits()
        events = getEvents()
    searchSubreddits = [ str(s.title) for s in Subreddit.objects.all()]
    return render(request, "index.html", {"posts" : posts, "popularsubreddits" : popularsubreddits,
                                          "events" : events, "searchSubreddits" : searchSubreddits })

top_sort_orders = ['','day', 'week', 'month','year','all']

def top(request, sort_type):
    if(sort_type in top_sort_orders):
        if(request.user.is_authenticated):
            posts = top_feed(sort_type,request.user)
            popularsubreddits = popularSubreddits(user=request.user)
            events = getEvents(request.user)
        else:
            posts = top_feed(sort_type)
            popularsubreddits = popularSubreddits()
            events = getEvents()

        return render(request, "index.html", {"posts" : posts, "popularsubreddits" : popularsubreddits,
                                          "events" : events})
    else:
       return redirect('index')

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
        events = getEventsByUser(username, request.user)
    else:
        userposts = userPosts(username)
        mypage = False
        events = getEventsByUser(username)
    return render(request, "user.html", {"posts" : userposts, "username" : username,
                                         "moderates" : moderated_subreddit, "mypage" : mypage,
                                         "ismoderator" : ismoderator, "events" : events})


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
        events = getEventsByUser(username, request.user)
    else:
        userposts = userVotedPosts(username, 1)
        mypage = False
        events = getEventsByUser(username)
    return render(request, "user.html", {"posts" : userposts, "username" : username,
                                         "moderates" : moderated_subreddit, "mypage" : mypage,
                                         "ismoderator" : ismoderator, "events" : events})

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
        mypage = request.user == view_user
        events = getEventsByUser(username, request.user)
    else:
        userposts = userVotedPosts(username, -1)
        mypage = False
        events = getEventsByUser(username)
    return render(request, "user.html", {"posts" : userposts, "username" : username,
                                         "moderates" : moderated_subreddit, "mypage" : mypage,
                                         "ismoderator" : ismoderator, "events" : events})

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

    for p in LinkPost.objects.filter(deleted = False).extra(select={'num_votes' : 0, \
        'num_comments' : 0, 'type' : '%s', 'vote' : 0}, select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(deleted = False).extra(select = {'num_votes' : 0, \
        'num_comments' : 0, 'type' : '%s', 'vote' : 0}, select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))

    return posts

def subsribed_feed(user):
    user_subreddits = set([s.subreddit for s in Subscriber.objects.filter(redditer=user)])
    posts = []

    for p in LinkPost.objects.filter(deleted = False).extra(select=
        {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, select_params=('link',)):
        if(p.posted_in in user_subreddits):
            posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(deleted = False).extra(select =
        {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},select_params = ('text',)):
        if(p.posted_in in user_subreddits):
            posts.append(updatePostFeatures(p, user))

    time_now = datetime.now()
    time_now = timezone.make_aware(time_now, timezone.get_current_timezone())

    return sorted(posts, key = lambda p: our_rank(p.num_votes, p.created_on,time_now), reverse=True)

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
    if(sort_type == 'day'):
        time_to_compare -= timedelta(days = 1)
    elif(sort_type == 'week'):
        time_to_compare -= timedelta(days = 7)
    elif(sort_type == 'month'):
        time_to_compare = monthdelta(time_to_compare, -1)
    elif(sort_type == 'year'):
        time_to_compare = monthdelta(time_to_compare, -12)
    elif(sort_type == 'all' or sort_type == ""):
        time_to_compare = epoch

    posts = []

    for p in LinkPost.objects.filter(created_on__gte=time_to_compare, deleted = False).\
        extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(created_on__gte=time_to_compare, deleted = False).\
        extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))
    return sorted(posts, key=lambda p: p.num_votes, reverse=True)

def userPosts(username, user = None):

    posts = []

    for p in LinkPost.objects.filter(posted_by__username=username,deleted = False).\
        extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(posted_by__username=username,deleted = False).\
        extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0},select_params = ('text',)):
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

def getEvents(user=None):
    events = []

    for e in Event.objects.all():
        if timezone.now() < e.time and checkSubscribed(user=user, subreddit=e.posted_in) and not e.deleted:
            events.append(e)

    return sorted(events, key=lambda e: e.time)

def getEventsByUser(username, user=None):
    events = []

    for e in Event.objects.filter(posted_by__username=username):
        if timezone.now() < e.time and not e.deleted:
            events.append(e)

    return sorted(events, key=lambda e: e.time)

def validate_username(username):
    return re.compile('[a-z0-9_]+$').match(username)