from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from .models import Dht22
from .serializers import *
from django.utils import timezone
import datetime
from services import models
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, BasePermission
from django.contrib.auth.models import Group, User
from django.db.models import Q
from rest_framework.decorators import authentication_classes, permission_classes
from django.http import HttpResponseBadRequest

# Create your views here.


# @login_required
# def get_dht22_info(request):
#     return

class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            user = User.objects.get(username=request.user)
        except Exception as ex:
            return False
        if user.groups.filter(Q(name='family') | Q(name="manager")) or user.is_staff:
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        return True
    
class Dht22APIHour(generics.ListAPIView):
    def get_queryset(self):
        date = datetime.now() - timedelta(hours=1)
        queryset = Dht22.objects.filter(date_create__gte=date).order_by('date_create')
        return queryset
    
    serializer_class = Dht22ListSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (CustomPermission, )
    
    
class Dht22APIDay(generics.ListAPIView):
    def get_queryset(self):
        date = datetime.now() - timedelta(days=1)
        queryset = Dht22.objects.filter(date_create__gte=date).order_by('date_create')
        return queryset
    
    serializer_class = Dht22ListSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (CustomPermission, )
    
    
class Dht22APIWeek(generics.ListAPIView):
    def get_queryset(self):
        date = datetime.now() - timedelta(weeks=1)
        queryset = Dht22.objects.filter(date_create__gte=date).order_by('date_create')
        return queryset
    
    serializer_class = Dht22ListSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (CustomPermission, )
    
    
@authentication_classes((TokenAuthentication, ))  
@permission_classes([CustomPermission, ])  
def dth22_current_date(request):
    date = datetime.now() - timedelta(minutes=5)
    queryset = Dht22.objects.filter(date_create__gte=date).order_by('-date_create')
    average_temperature = 0
    average_humidity = 0
    count = queryset.count()
    if count == 0:
        raise HttpResponseBadRequest
    for q in queryset:
        average_temperature += q.temperature
        average_humidity += q.humidity
    average_temperature = round(average_temperature / count, 1)
    average_humidity = round(average_humidity / count, 1)
    return JsonResponse({'temperature': average_temperature, 'humidity': average_humidity}, safe=False)
