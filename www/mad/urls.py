from django.urls import path
from django.contrib.staticfiles.urls import static
from django.conf import settings
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('more/', views.more, name='more'),
    path('inner_detail/', views.inner_detail, name='inner_detail'),
    path('outer_detail/', views.outer_detail, name='outer_detail'),
    path('ua_detail/', views.ua_detail, name='ua_detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
