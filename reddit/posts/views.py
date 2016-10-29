from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, you're at the posts page!")