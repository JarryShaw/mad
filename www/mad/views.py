from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import *


# Create your views here.
def index(request):
    template = loader.get_template('pages/index.html')
    context = {}
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the index.")


def more(request):
    template = loader.get_template('pages/more.html')
    context = {
        "reports": [
            {
                "time": "123",
                "srcIP": "123",
                "dstIP": "123",
                "srcPort": "123",
                "dstPort": "123",
                "UA": "123"
            },
            {
                "time": "456",
                "srcIP": "456",
                "dstIP": "456",
                "srcPort": "456",
                "dstPort": "456",
                "UA": "456"
            }
        ]
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the more.")


def inner_detail(request):
    template = loader.get_template('pages/inner_detail.html')
    context = {}
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the inner details.")


def outer_detail(request):
    template = loader.get_template('pages/outer_detail.html')
    context = {}
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the outer details.")


def ua_detail(request):
    template = loader.get_template('pages/ua_detail.html')
    context = {}
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the ua details.")
