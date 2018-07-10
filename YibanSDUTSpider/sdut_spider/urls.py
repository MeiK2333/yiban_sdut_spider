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
    path('borrow/info/', views.borrow),
    path('borrow/history/', views.borrow_history),
    path('dorm_health/', views.dorm_health),
    path('cust_state_info/', views.cust_state_info),
    path('cust_state_info/<int:delta>/', views.cust_state_info),
    path('schedule/', views.schedule),
    path('schedule/<int:cur>/', views.schedule),
]
