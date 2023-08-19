from django.contrib import admin
from django.urls import path
from .views import *



urlpatterns = [
    path('hour/', Dht22APIHour.as_view(), name="dht22_hour"),
    path('day/', Dht22APIDay.as_view(), name="dht22_day"),
    path('week/', Dht22APIWeek.as_view(), name="dht22_month"),
    path('current/', dth22_current_date, name="dht22_current"),
    
]
