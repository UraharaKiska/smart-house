from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, BasePermission
from django.contrib.auth.models import Group, User
from rest_framework import generics
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from .serializers import GroupSerializer, UserGroupSerializer
from rest_framework.views import APIView

# Create your views here.



class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            user = User.objects.get(username=request.user)
        except Exception as ex:
            return False
        if user.groups.filter(name='manager') or user.is_staff == True:
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        return True
    

class GroupsAPIView(APIView):
    
    permission_classes = (IsManagerOrAdmin, )
    
    
    def get(self, request):
        groups = Group.objects.all()
        return Response({'groups': GroupSerializer(groups, many=True).data})
    
    
    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': serializer.data})
    
    
class AddUserToGroup(APIView):
    permission_classes = (IsManagerOrAdmin,  )
    
    
    def post(self, request):
        serializer = UserGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        try:
            user = User.objects.get(username=data['username'])
            group = Group.objects.get(name=data['group'])
            user.groups.add(group)
            user.save
            return Response({'detail': serializer.data})
        except Exception as ex:
            return Response({'detail': {"user or group dose't exist"}})
            
            
    