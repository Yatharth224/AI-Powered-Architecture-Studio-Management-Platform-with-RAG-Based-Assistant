# services/serializers.py

from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Service
        fields = [
            'id',
            'title',
            'description',
            'category',
            'price_range',
            'image',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']