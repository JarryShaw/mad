# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import Mad_Report


# Create your views here.
def index(request):
    template = loader.get_template('pages/index.html')
    context = {}
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the index.")


def more(request):
    template = loader.get_template('pages/more.html')
    context = {
        "reports": Mad_Report.objects.filter(is_malicious=True).order_by('id')  # pylint: disable=E1101
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
    context = {
        "reports": []
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the ua details.")
