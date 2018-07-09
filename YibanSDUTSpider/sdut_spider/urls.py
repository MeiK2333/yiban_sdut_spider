from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'API'
urlpatterns = [
    path('card/balance/', views.card_balance),
    path('card/info/', views.card_info),
    path('energy/', views.energy),
    path('energy/info/', views.energy_info),
]
