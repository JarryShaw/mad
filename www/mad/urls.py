# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('more/', views.more, name='more'),
    path('inner/', views.innerIp, name='innerIp'),
    path('inner/<str:srcIP>/', views.innerDetail, name='innerDetail'),
    path('outer/', views.outerIp, name='outerIp'),
    path('outer/<str:dstIP>/', views.outerDetail, name='outerDetail'),
    path('ua/', views.ua, name='ua'),
    path('ua/<path:userAgent>/', views.uaDetail, name='uaDetail'),
    path('connection/<str:srcIP>/<str:dstIP>/', views.connection, name='connection'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
