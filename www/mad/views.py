from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the index.")


def more(request):
    return HttpResponse("Hello, world. You're at the more.")


def inner_detail(request):
    return HttpResponse("Hello, world. You're at the inner details.")


def outer_detail(request):
    return HttpResponse("Hello, world. You're at the outer details.")


def ua_detail(request):
    return HttpResponse("Hello, world. You're at the ua details.")
