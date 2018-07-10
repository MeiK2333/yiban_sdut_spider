from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'YibanSdut'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('yiban_login/', views.yiban_login, name='yiban_login'),
]
