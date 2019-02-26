# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.db.models import Count, Sum, Max, Min

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
        "reports": Mad_Report.objects.order_by('id').values("srcip", "srcport", "dstip", "dstport", "ua", "time", "is_malicious")
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the more.")


def innerIp(request):
    template = loader.get_template('pages/innerIp.html')
    context = {
        "reports": Mad_Report.objects.values("srcip").annotate(ua_num=Count("id"), malicious=Sum("is_malicious"))
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the inner details.")


def innerDetail(request, srcIP):
    template = loader.get_template('pages/inner_detail.html')
    context = {
        "srcIP": srcIP,
        "outers": Mad_Report.objects.filter(srcip=srcIP).values("ua", "dstip", "is_malicious").annotate(stime=Min("time"), etime=Max("time"))
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the inner details.")


def outerIp(request):
    template = loader.get_template('pages/outerIp.html')
    context = {
        "reports": Mad_Report.objects.values("dstip").annotate(stime=Min("time"), etime=Max("time"), malicious=Sum("is_malicious"))
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the outer details.")


def outerDetail(request, dstIP):
    template = loader.get_template('pages/outer_detail.html')
    context = {
        "dstIP": dstIP,
        "is_malicious": Mad_Report.objects.filter(dstip=dstIP).values("is_malicious").distinct(),
        "inners": Mad_Report.objects.filter(dstip=dstIP).values("ua", "srcip").annotate(stime=Min("time"), etime=Max("time"))
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the outer details.")


def ua(request):
    template = loader.get_template('pages/ua.html')
    context = {
        "reports": Mad_Report.objects.values("ua").annotate(stime=Min("time"), etime=Max("time"), malicious=Sum("is_malicious"))
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the ua details.")


def uaDetail(request, userAgent):
    template = loader.get_template('pages/ua_detail.html')
    context = {
        "info": Mad_Report.objects.filter(ua=userAgent).values("ua", "device", "os", "browser", "type")[:1],
        "connections": Mad_Report.objects.filter(ua=userAgent).values("srcip", "srcport", "dstip", "dstport", "is_malicious").annotate(stime=Min("time"), etime=Max("time"))
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the ua details.")


def connection(request, srcIP, dstIP):
    template = loader.get_template('pages/connection.html')
    context = {
        "srcIP": srcIP,
        "dstIP": dstIP,
        "connections": Mad_Report.objects.filter(dstip=dstIP, srcip=srcIP).values("time", "url", "ua", "srcport", "dstport", "is_malicious", "detected_by_cnn")
    }
    return HttpResponse(template.render(context, request))
