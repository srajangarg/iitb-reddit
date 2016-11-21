from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from subreddits.models import Subreddit
from posts.models import TextPost, LinkPost, Comment, Vote
from posts.views import updatePostFeatures
import ldap

def index(request):
    if request.user.is_authenticated():
        posts = feed(request.user)
    else:
        posts = feed()
    return render(request, "index.html", {"posts" : posts})

def login(request):

    if request.method == 'GET':
        return redirect('index')
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        auth_login(request, user)
        return redirect('index')
    else:
        return HttpResponse("Invalid credentials")


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
        user = get_user_model().objects.create_user(username, email, password)
        if user is not None:
            return HttpResponse("Successfully Signed Up!")

    return HttpResponse("Can't sign Up!")

def logout(request):

    auth_logout(request)
    return redirect('index')

def user(request, username):
    if request.user.is_authenticated():
        userposts = userfeed(username, request.user)
    else:
        userposts = userfeed(username)
    return render(request, "user.html", {"posts" : userposts})

# def myaccount(request):
# 
#     if request.user.is_authenticated():
#         user_email = request.user.email
#         return redirect('user/' + user_email)
#     else:
#         return redirect('index')

def feed(user = None):

    posts = []

    for p in LinkPost.objects.extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.extra(select = {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))

    return sorted(posts, key = lambda p: p.num_votes, reverse=True)


def userfeed(username, user = None):

    posts = []

    for p in LinkPost.objects.filter(posted_by__email = username).extra(select={'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params=('link',)):
        posts.append(updatePostFeatures(p, user))

    for p in TextPost.objects.filter(posted_by__email = username).extra(select = {'num_votes' : 0, 'num_comments' : 0, 'type' : '%s', 'vote' : 0}, 
                                    select_params = ('text',)):
        posts.append(updatePostFeatures(p, user))

    return sorted(posts, key = lambda p: p.num_votes, reverse=True)
