from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login

def index(request):
    if request.user.is_authenticated():
        user_email = request.user.email
        return HttpResponse("Hello %s" % user_email);
    else:
        return HttpResponse("Hello, you're not logged in!")

def login(request):
    # test
    user = authenticate(email="garg@iitb.ac.in", password="garg123")
    if user is not None:
        auth_login(request, user)
        return HttpResponse("Logged In!")
    else:
        return HttpResponse("Invalid credentials")