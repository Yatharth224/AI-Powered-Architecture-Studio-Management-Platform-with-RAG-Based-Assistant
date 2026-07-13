from rest_framework import serializers
from django.contrib.auth.models import User
from  .models import ArchitectInvite


User = get_user_model()

class ArchitectInviteSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True,min_length=8)
    confirm_password = serializers.CharField(write_only=True)


    