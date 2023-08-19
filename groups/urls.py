from django.contrib import admin
from django.urls import path, include, re_path
from .views import GroupsAPIView, AddUserToGroup


urlpatterns = [
    path('', GroupsAPIView.as_view(), name="groups"),
    path('adduser/', AddUserToGroup.as_view())
    # path('user', some,),
    
    
]