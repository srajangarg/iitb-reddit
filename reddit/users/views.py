from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated():
        user_email = request.user.email
        return render(request, "index.html", {"username":user_email})
    else:
        return render(request, "index.html")

def login(request):
    email = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
        auth_login(request, user)
        return render(request, "index.html",{"username":email})
    else:
        return HttpResponse("Invalid credentials")

def signup(request):
    email = request.POST['email']
    password = request.POST['password']

    user = get_user_model().objects.create_user(email, password)
    if user is not None:
        return HttpResponse("Successfully Signed Up!")
    else:
        return HttpResponse("Can't sign Up!")

def logout(request):
    auth_logout(request)
    return redirect('index')

def user(request, username):
    return render(request, "user.html")

# def myaccount(request):
#     if request.user.is_authenticated():
#         user_email = request.user.email
#         return redirect('user/' + user_email)
#     else:
#         return redirect('index')


# POST
#     postID
#     heading
#     user
#     subreddit
#     timestamp
#     num_comments
#     num_upvotes