# projects/serializers.py

from rest_framework import serializers
from .models import Project, Milestone
from users.serializers import UserProfileSerializer


class MilestoneSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Milestone
        fields = [
            'id',
            'title',
            'description',
            'status',
            'due_date',
            'completed_at'
        ]
        read_only_fields = ['id']


class ProjectSerializer(serializers.ModelSerializer):
    # Nested serializer — project ke saath milestones bhi aayenge
    milestones = MilestoneSerializer(many=True, read_only=True)

    # Client aur architect ka naam bhi dikhao
    client_name   = serializers.CharField(source='client.username',   read_only=True)
    architect_name = serializers.CharField(source='architect.username', read_only=True, allow_null=True)

    class Meta:
        model  = Project
        fields = [
            'id',
            'title',
            'description',
            'status',
            'budget',
            'location',
            'client',
            'client_name',
            'architect',
            'architect_name',
            'milestones',
            'start_date',
            'end_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Project banane ke liye alag serializer
    Admin use karega
    """
    class Meta:
        model  = Project
        fields = [
            'title',
            'description',
            'status',
            'budget',
            'location',
            'client',
            'architect',
            'start_date',
            'end_date'
        ]


class AssignArchitectSerializer(serializers.ModelSerializer):
    """
    Architect assign karne ke liye
    Sirf architect field update hoga
    """
    class Meta:
        model  = Project
        fields = ['architect']