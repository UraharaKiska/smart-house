from rest_framework import serializers
from .models import Dht22


class Dht22ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dht22
        fields = "__all__"

