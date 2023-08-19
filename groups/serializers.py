from rest_framework import serializers
from django.contrib.auth.models import Group, User



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name"]

    def create(self, validate_data):
        return Group.objects.create(**validate_data)
    
    
class UserGroupSerializer(serializers.Serializer):
    username = serializers.CharField()
    group = serializers.CharField()
    
    
    